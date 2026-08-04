import Navbar from "../../components/Navbar/Navbar";
import Footer from "../../components/Footer/Footer";
import { Outlet } from "react-router-dom";

export default function Home({ email }) {
  return (
    <>
      <Navbar email={email} />
      <Outlet />
      <Footer />
    </>
  );
}