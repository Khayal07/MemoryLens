import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Layout from "./components/Layout";
import Protected from "./components/Protected";
import CategorySelect from "./pages/CategorySelect";
import History from "./pages/History";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Search from "./pages/Search";

const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: "/", element: <CategorySelect /> },
      { path: "/search/:category", element: <Search /> },
      { path: "/login", element: <Login /> },
      { path: "/register", element: <Register /> },
      {
        path: "/history",
        element: (
          <Protected>
            <History />
          </Protected>
        ),
      },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
