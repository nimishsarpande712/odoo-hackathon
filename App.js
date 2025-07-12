import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import Register from './components/Register';
import Login from './components/Login';
import Profile from './components/Profile';
import Dashboard from './components/Dashboard';
import AllProfiles from './components/AllProfiles';
import EmailVerification from './components/EmailVerification';
import ForgotPassword from './components/ForgotPassword';
import ResetPassword from './components/ResetPassword';
import AdminLogin from './components/AdminLogin';
import SearchUsers from './components/SearchUsers';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/all-profiles" element={<AllProfiles />} />
            <Route path="/verify-email" element={<EmailVerification />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/admin" element={<AdminLogin />} />
            <Route path="/search" element={<SearchUsers />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
