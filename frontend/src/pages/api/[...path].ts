import type { NextApiRequest, NextApiResponse } from "next";
import { getToken } from "next-auth/jwt";

const getJwt = async (req: NextApiRequest) => {
  return await getToken({ req, secret: process.env.NEXTAUTH_SECRET });
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const jwt = await getJwt(req);

  const { path } = req.query;
  const method = req.method;
  const headers = new Headers(req.headers as Record<string, string>);
  const body = req.body;

  const apiBaseUrl = process.env.API_URL;
  const forwardPath = Array.isArray(path) ? path.join("/") : path;
  const forwardUrl = `${apiBaseUrl}/${forwardPath}`;

  try {
    let forwardedBody = body;
    if (method !== "GET" && method !== "DELETE") {
      if (headers.get("Content-Type")?.includes("application/json") && body) {
        forwardedBody = JSON.stringify(body);
      }
    }

    if (method === "GET") {
      forwardedBody = undefined;
    }

    if (jwt?.access_token) {
      headers.set("Authorization", `Bearer ${jwt.access_token}`);
    }

    const response = await fetch(forwardUrl, {
      method: method,
      headers: headers,
      body: forwardedBody,
    });

    if (!response.ok || response.status >= 400) {
      const data = await response.json();
      res.status(response.status).send({ error: `Error: ${data.detail}` });
      return;
    }

    const responseBody = await response.json();
    res.setHeader(
      "Content-Type",
      response.headers.get("Content-Type") || "application/json"
    );
    res.status(response.status).send(responseBody);
  } catch (error) {
    console.error("Error forwarding request:", error);
    res.status(500).json({ error: "Internal Server Error" });
  }
}
