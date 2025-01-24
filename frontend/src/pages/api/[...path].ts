import type { NextApiRequest, NextApiResponse } from "next";
import { getToken } from "next-auth/jwt";
import axios, { AxiosError } from "axios";

const getJwt = async (req: NextApiRequest) => {
  return await getToken({ req, secret: process.env.NEXTAUTH_SECRET });
};

const api = axios.create({
  baseURL: process.env.API_URL,
});

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const jwt = await getJwt(req);

  const { path } = req.query;
  const method = req.method;
  const headers = new Headers(req.headers as Record<string, string>);
  const body = req.body;

  const forwardPath = Array.isArray(path) ? path.join("/") : path;

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

    const headersObject = Object.fromEntries(headers.entries());
    let response;

    try {
      response = await api.request({
        method: method,
        url: forwardPath,
        headers: headersObject,
        data: forwardedBody,
      });
    } catch (error: unknown) {
      if (error instanceof AxiosError) {
        console.log(error.response?.headers);
        if (
          error.response?.status === 401 &&
          jwt &&
          error.response?.headers["expired"]
        ) {
          res.status(307).json({ url: "/auth/signout" });
          return;
        }

        if (error.response?.status && error.response?.status >= 400) {
          res
            .status(error.response?.status)
            .send({ error: `Error: ${error.response?.data.detail}` });
          return;
        }
      }
    }

    if (!response) {
      res.status(500).json({ error: "Internal Server Error" });
      return;
    }

    const responseBody = response.data;
    res.setHeader(
      "Content-Type",
      response.headers["content-type"] || "application/json"
    );
    res.status(response.status).send(responseBody);
  } catch (error) {
    console.error("Error forwarding request:", error);
    res.status(500).json({ error: "Internal Server Error" });
  }
}
