import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import AuthCard from "./AuthCard";
import AuthInput from "./AuthInput";
import AuthButton from "./AuthButton";
import { loginUser } from "../helpers/api-communicator";

interface LoginboxProps {
  onLoginSuccess: () => void;
}

const Loginbox: React.FC<LoginboxProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    toast.loading("Signing you in...", { id: "login" });

    try {
      const data = await loginUser(email, password);

      localStorage.setItem("token", data.token);
      toast.success("Welcome back! Redirecting to chat...", { id: "login" });
      onLoginSuccess();
      navigate("/chatpage");
    } catch (err) {
      console.error("Login failed:", err);
      const errorMessage = err instanceof Error ? err.message : "Invalid username or password. Please try again.";
      setError(errorMessage);
      toast.error(errorMessage, { id: "login" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthCard title="Welcome Back">
      <form onSubmit={handleSubmit}>
        <AuthInput
          type="email"
          name="email"
          placeholder="Email or Phone"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoComplete="email"
          label="Username"
          error={error}
        />

        <AuthInput
          type="password"
          name="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete="current-password"
          label="Password"
        />

        <AuthButton
          type="submit"
          loading={isLoading}
          disabled={isLoading}
          variant="primary"
        >
          {isLoading ? "Logging in..." : "Log In"}
        </AuthButton>
      </form>
    </AuthCard>
  );
};

export default Loginbox;