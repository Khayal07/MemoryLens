import { lazy } from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Layout from "./components/Layout";
import Protected from "./components/Protected";

// Route-level code splitting — each page ships in its own chunk.
const CategorySelect = lazy(() => import("./pages/CategorySelect"));
const Search = lazy(() => import("./pages/Search"));
const Login = lazy(() => import("./pages/Login"));
const Register = lazy(() => import("./pages/Register"));
const History = lazy(() => import("./pages/History"));
const Collections = lazy(() => import("./pages/Collections"));
const SharedResult = lazy(() => import("./pages/SharedResult"));
const Analytics = lazy(() => import("./pages/Analytics"));

const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: "/", element: <CategorySelect /> },
      { path: "/search/:category", element: <Search /> },
      { path: "/login", element: <Login /> },
      { path: "/register", element: <Register /> },
      { path: "/s/:token", element: <SharedResult /> },
      {
        path: "/history",
        element: (
          <Protected>
            <History />
          </Protected>
        ),
      },
      {
        path: "/collections",
        element: (
          <Protected>
            <Collections />
          </Protected>
        ),
      },
      {
        path: "/analytics",
        element: (
          <Protected>
            <Analytics />
          </Protected>
        ),
      },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
