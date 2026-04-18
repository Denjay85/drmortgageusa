import { sql } from "drizzle-orm";
import { pgTable, text, varchar, decimal, boolean, timestamp, integer } from "drizzle-orm/pg-core";
import { createInsertSchema, createSelectSchema } from "drizzle-zod";
import { z } from "zod";

export const leads = pgTable("leads", {
  id: varchar("id", { length: 50 }).primaryKey().default(sql`gen_random_uuid()`),
  name: text("name").notNull(),
  email: text("email").notNull(),
  phone: text("phone"),
  yearBought: integer("year_bought"),
  savingsGoal: decimal("savings_goal", { precision: 10, scale: 2 }),
  currentRate: text("current_rate"),
  consent: boolean("consent").notNull(),
  source: text("source").default("rate-watch"),
  utmData: text("utm_data"),
  status: text("status").default("active"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const insertLeadSchema = createInsertSchema(leads, {
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Invalid email address"),
  phone: z.string().optional(),
  yearBought: z.number().optional(),
  savingsGoal: z.number().optional(),
  currentRate: z.string().min(1, "Please provide your current interest rate or best guess"),
  consent: z.boolean().refine(val => val === true, "Consent is required"),
}).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export const selectLeadSchema = createSelectSchema(leads);

export type InsertLead = z.infer<typeof insertLeadSchema>;
export type Lead = typeof leads.$inferSelect;

// Mortgage rate history table for tracking rate changes over time
export const rateHistory = pgTable("rate_history", {
  id: varchar("id", { length: 50 }).primaryKey().default(sql`gen_random_uuid()`),
  rateType: text("rate_type").notNull(), // "30-year-fixed", "15-year-fixed", "5-1-arm", etc.
  rate: decimal("rate", { precision: 5, scale: 3 }).notNull(), // e.g., 6.875
  source: text("source").default("manual"), // "freddie-mac", "manual", etc.
  effectiveDate: timestamp("effective_date").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertRateHistorySchema = createInsertSchema(rateHistory, {
  rateType: z.string().min(1, "Rate type is required"),
  rate: z.number().min(0).max(20),
  effectiveDate: z.date(),
}).omit({
  id: true,
  createdAt: true,
});

export const selectRateHistorySchema = createSelectSchema(rateHistory);

export type InsertRateHistory = z.infer<typeof insertRateHistorySchema>;
export type RateHistory = typeof rateHistory.$inferSelect;

// Refinance alerts table for tracking when alerts are sent to leads
export const refinanceAlerts = pgTable("refinance_alerts", {
  id: varchar("id", { length: 50 }).primaryKey().default(sql`gen_random_uuid()`),
  leadId: varchar("lead_id", { length: 50 }).notNull().references(() => leads.id),
  triggerRate: decimal("trigger_rate", { precision: 5, scale: 3 }).notNull(),
  projectedSavings: decimal("projected_savings", { precision: 10, scale: 2 }).notNull(),
  emailSent: boolean("email_sent").default(false).notNull(),
  emailSentAt: timestamp("email_sent_at"),
  alertType: text("alert_type").default("savings-threshold"), // "savings-threshold", "rate-drop", etc.
  calculationDetails: text("calculation_details"), // JSON string with detailed analysis
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertRefinanceAlertSchema = createInsertSchema(refinanceAlerts, {
  leadId: z.string().min(1, "Lead ID is required"),
  triggerRate: z.number().min(0).max(20),
  projectedSavings: z.number().min(0),
}).omit({
  id: true,
  createdAt: true,
});

export const selectRefinanceAlertSchema = createSelectSchema(refinanceAlerts);

export type InsertRefinanceAlert = z.infer<typeof insertRefinanceAlertSchema>;
export type RefinanceAlert = typeof refinanceAlerts.$inferSelect;
