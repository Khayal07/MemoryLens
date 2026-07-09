import { lazy } from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Layout from "./components/Layout";
import Protected from "./components/Protected";
import { useAuth } from "./features/auth/AuthContext";

// Route-level code splitting — each page ships in its own chunk.
const CategorySelect = lazy(() => import("./pages/CategorySelect"));
const Search = lazy(() => import("./pages/Search"));
const Login = lazy(() => import("./pages/Login"));
const Register = lazy(() => import("./pages/Register"));
const History = lazy(() => import("./pages/History"));
const Collections = lazy(() => import("./pages/Collections"));
const SharedResult = lazy(() => import("./pages/SharedResult"));
const Analytics = lazy(() => import("./pages/Analytics"));
const Constellation = lazy(() => import("./pages/Constellation"));
const Challenge = lazy(() => import("./pages/Challenge"));
const Landing = lazy(() => import("./pages/Landing"));

/** Signed-in users land on the category grid; visitors get the cinematic story. */
function HomeGate() {
  const { isAuthenticated, ready } = useAuth();
  if (!ready) return null; // AuthProvider is still restoring the session
  return isAuthenticated ? <CategorySelect /> : <Landing />;
}

const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: "/", element: <HomeGate /> },
      {
        path: "/search/:category",
        element: (
          <Protected to="/register">
            <Search />
          </Protected>
        ),
      },
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
      {
        path: "/constellation",
        element: (
          <Protected>
            <Constellation />
          </Protected>
        ),
      },
      {
        path: "/challenge",
        element: (
          <Protected>
            <Challenge />
          </Protected>
        ),
      },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
