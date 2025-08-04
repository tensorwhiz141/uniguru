import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-hot-toast";
import AuthCard from "./AuthCard";
import AuthInput from "./AuthInput";
import AuthButton from "./AuthButton";
import GoogleOAuthProduction from "./GoogleOAuthProduction";
import { signupUser, loginWithGoogle } from "../helpers/api-communicator";

type FormData = {
  name: string;
  email: string;
  password: string;
};



interface FieldErrors {
  name?: string;
  email?: string;
  password?: string;
  general?: string;
}

const Signupbox: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<FormData>({
    name: "",
    email: "",
    password: "",
  });

  const [errors, setErrors] = useState<FieldErrors>({});
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    // Clear specific field error when user starts typing
    if (errors[name as keyof FieldErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: FieldErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = "Name is required";
    } else if (formData.name.trim().length < 2) {
      newErrors.name = "Name must be at least 2 characters";
    }

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      toast.loading("Creating your account...", { id: "signup" });

      const response = await signupUser(formData.name, formData.email, formData.password);

      if (response.success) {
        toast.success("Account created successfully! Please login to continue.", { id: "signup" });
        // Reset form
        setFormData({ name: "", email: "", password: "" });
        // Redirect to login page after a short delay
        setTimeout(() => {
          navigate("/login");
        }, 1500);
      }
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Signup failed. Please try again.";

      // Check if error is field-specific
      if (errorMessage.toLowerCase().includes('email')) {
        setErrors({ email: errorMessage });
      } else if (errorMessage.toLowerCase().includes('password')) {
        setErrors({ password: errorMessage });
      } else if (errorMessage.toLowerCase().includes('name')) {
        setErrors({ name: errorMessage });
      } else {
        setErrors({ general: errorMessage });
      }

      toast.error(errorMessage, { id: "signup" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSuccess = async (credential: string) => {
    setIsLoading(true);
    setErrors({});
    toast.loading("Creating account with Google...", { id: "google-signup" });

    try {
      const data = await loginWithGoogle(credential);

      localStorage.setItem("token", data.token);
      toast.success("Account created successfully! Redirecting to chat...", { id: "google-signup" });

      // Redirect to chat page after successful Google signup/login
      setTimeout(() => {
        navigate("/chatpage");
      }, 1500);
    } catch (err) {
      console.error("Google signup failed:", err);
      const errorMessage = err instanceof Error ? err.message : "Google authentication failed. Please try again.";
      setErrors({ general: errorMessage });
      toast.error(errorMessage, { id: "google-signup" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleError = (error: any) => {
    console.error("Google OAuth error:", error);
    setErrors({ general: "Google authentication failed. Please try again." });
    toast.error("Google authentication failed. Please try again.", { id: "google-signup" });
  };

  return (
    <AuthCard title="Create Account">
      <form onSubmit={handleSubmit}>
        <AuthInput
          type="text"
          name="name"
          placeholder="Full Name"
          value={formData.name}
          onChange={handleChange}
          required
          autoComplete="name"
          label="Name"
          error={errors.name}
        />

        <AuthInput
          type="email"
          name="email"
          placeholder="Email Address"
          value={formData.email}
          onChange={handleChange}
          required
          autoComplete="email"
          label="Email"
          error={errors.email}
        />

        <AuthInput
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
          required
          autoComplete="new-password"
          label="Password"
          error={errors.password}
        />

        {/* General error message */}
        {errors.general && (
          <p className="text-red-400 text-sm font-medium mt-4 font-poppins">
            {errors.general}
          </p>
        )}

        <AuthButton
          type="submit"
          loading={isLoading}
          disabled={isLoading}
          variant="primary"
        >
          {isLoading ? "Creating Account..." : "Sign Up"}
        </AuthButton>

        {/* Divider */}
        <div className="flex items-center my-6">
          <div className="flex-1 border-t border-gray-600"></div>
          <span className="px-4 text-gray-400 text-sm">or</span>
          <div className="flex-1 border-t border-gray-600"></div>
        </div>

        {/* Google OAuth Button */}
        <div className="relative">
          <GoogleOAuthProduction
            onSuccess={handleGoogleSuccess}
            onError={handleGoogleError}
            disabled={isLoading}
            text="Sign up with Google"
            className="w-full"
          />
        </div>
      </form>
    </AuthCard>
  );
};

export default Signupbox;
