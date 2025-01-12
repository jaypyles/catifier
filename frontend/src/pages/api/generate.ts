import { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method === 'POST') {
        const data = req.body; 
        console.log(data)

        const response = await fetch(`${process.env.GOOGLE_CLOUD_RUN_URL}/generate`, {
            method: 'POST',
            body: data,
            headers: {
                'Content-Type': 'application/json',
            },
        })

        const result = await response.json()

        res.status(200).json({ success: true, result: result.image_url });
    } else {
        res.setHeader('Allow', ['POST']);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
}