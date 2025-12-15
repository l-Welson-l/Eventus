import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import RegisterSelect from "./pages/RegisterSelect";
import RegisterCustomer from "./pages/RegisterCustomer";
import RegisterBusiness from "./pages/RegisterBusiness";
import Login from "./pages/LoginPage";

function App() {
  return (
    <Routes>
      <Route path="/register" element={<RegisterSelect />} />
      <Route path="/register/customer" element={<RegisterCustomer />} />
      <Route path="/register/business" element={<RegisterBusiness />} />
      <Route path="/login" element={<Login />} />
    </Routes>
  );
}

export default App;
