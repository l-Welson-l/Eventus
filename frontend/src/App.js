import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import RegisterSelect from "./pages/RegisterSelect";
import RegisterCustomer from "./pages/RegisterCustomer";
import RegisterBusiness from "./pages/RegisterBusiness";
import Login from "./pages/LoginPage";
import Dashboard from "./pages/Dashboard";
import AuthDebugPage from "./pages/AuthDebugPage";
import MagicLogin from "./pages/MagicLogin";

import EventJoin from "./pages/EventJoin";
import EventPage from "./pages/EventPage";
import CreateEvent from "./pages/CreateEvent";
import EditEvent from "./pages/EditEvent";

function App() {
  return (
    <Routes>
      <Route path="/register" element={<RegisterSelect />} />
      <Route path="/register/customer" element={<RegisterCustomer />} />
      <Route path="/register/business" element={<RegisterBusiness />} />
      <Route path="/login" element={<Login />} />

      <Route path="/auth-debug" element={<AuthDebugPage />} />
      <Route path="/magic-login" element={<MagicLogin />} />
      <Route path="/dashboard" element={<Dashboard />} />


      <Route path="/event/join/:eventId" element={<EventJoin />} />
      <Route path="/event/:eventId" element={<EventPage />} />
      <Route path="/events/create" element={<CreateEvent />} />
      <Route path="/events/:id/edit" element={<EditEvent />} />



    </Routes>
  );
}

export default App;
