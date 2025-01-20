import NextAuth from "next-auth";

declare module "next-auth" {
  interface Session {
    user: {
      id: string;
      username: string;
      [key: string]: any;  
    };
  }

  interface User {
    id: string;
    username: string;
    [key: string]: any;  
  }
}
