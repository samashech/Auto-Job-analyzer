import { z } from "zod";

const nameRegex = /^[A-Za-z ]+$/;
const phoneRegex = /^[0-9]{10,14}$/;

export const authSignupSchema = z
  .object({
    fullName: z
      .string()
      .min(2, "Name is required.")
      .regex(nameRegex, "Name must contain only alphabetic characters and spaces."),
    email: z.email("Please enter a valid email address."),
    password: z.string().min(8, "Password must be at least 8 characters."),
    confirmPassword: z.string().min(8),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match.",
    path: ["confirmPassword"],
  });

export const authLoginSchema = z.object({
  email: z.email("Please enter a valid email."),
  password: z.string().min(1, "Password is required."),
});

export const forgotPasswordSchema = z.object({
  email: z.email("Please enter your registered email."),
});

export const profileSchema = z.object({
  fullName: z
    .string()
    .min(2, "Full name is required.")
    .regex(nameRegex, "Name must contain only alphabetic characters and spaces."),
  email: z.email("Enter a valid email."),
  phone: z.string().regex(phoneRegex, "Phone must be digits only (10-14 digits)."),
  about: z.string().min(20, "About Me should be at least 20 characters."),
  skills: z.string().min(3, "Provide at least one skill."),
  projects: z.string().min(3, "Provide at least one project."),
  achievements: z.string().min(3, "Provide at least one achievement."),
  education: z.string().min(3, "Provide education details."),
  positionsOfResponsibility: z.string().min(3, "Provide at least one position of responsibility."),
  certificates: z.string().min(3, "Provide at least one certificate."),
  linkedIn: z.url("LinkedIn URL is invalid."),
  github: z.url("GitHub URL is invalid."),
  portfolio: z.url("Portfolio URL is invalid."),
});

export type AuthSignupValues = z.infer<typeof authSignupSchema>;
export type AuthLoginValues = z.infer<typeof authLoginSchema>;
export type ForgotPasswordValues = z.infer<typeof forgotPasswordSchema>;
export type ProfileFormValues = z.infer<typeof profileSchema>;
