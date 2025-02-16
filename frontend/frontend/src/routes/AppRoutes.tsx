import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SignIn from "../pages/sign-in/SignIn";
import SignUp from "../pages/sign-up/SignUp";
import MainPage from "../pages/MainPage";

const AppRoutes = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/mainpage" element={<MainPage />} />

      </Routes>
    </Router>
  );
};

export default AppRoutes;
