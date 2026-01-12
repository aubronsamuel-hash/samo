export type UUID = string;

export type UserRole = "admin" | "manager" | "technician";

export interface User {
  id: UUID;
  email: string;
  phone?: string | null;
  first_name?: string | null;
  last_name?: string | null;
  roles: UserRole[];
  specializations: Record<string, unknown>[];
  availability: Record<string, string[]>;
  employment_contract: Record<string, unknown>;
}

export interface BreakTime {
  start: string;
  end: string;
  mandatory?: boolean;
}

export interface ResourceItem {
  id: UUID;
  type: string;
  role?: string | null;
  required_skills: string[];
  quantity: number;
}

export interface EconomicValueBreakdown {
  labor_cost?: number | null;
  equipment_cost?: number | null;
  transport_cost?: number | null;
  meal_allowance?: number | null;
  overtime_cost?: number | null;
}

export interface EconomicValue {
  base_rate: number;
  budget_line: string;
  total_amount?: number | null;
  equipment_rate?: number | null;
  breakdown?: EconomicValueBreakdown | null;
}

export interface ShiftMetadata {
  technical_rider?: string | null;
  stage_plot?: string | null;
  cable_plan?: string | null;
}

export type ShiftStatus =
  | "draft"
  | "planned"
  | "confirmed"
  | "call_issued"
  | "in_progress"
  | "break"
  | "completed"
  | "cancelled"
  | "postponed";

export interface ShiftCreate {
  title: string;
  description?: string | null;
  event_id: UUID;
  call_time?: string | null;
  start_time: string;
  end_time: string;
  break_times: BreakTime[];
  resources: ResourceItem[];
  economic_value: EconomicValue;
  priority: string;
  metadata?: ShiftMetadata | null;
}

export interface ConflictItem {
  resource_id: UUID;
  resource_type: string;
  shift_id?: UUID | null;
  severity: string;
}

export interface WarningItem {
  code: string;
  message: string;
  severity: string;
}

export interface Shift {
  id: UUID;
  event_id: UUID;
  status: ShiftStatus;
  conflicts: ConflictItem[];
  warnings: WarningItem[];
  economic_value: Record<string, unknown>;
  created_at?: string | null;
  version: number;
}

export type EquipmentStatus = "available" | "booked" | "maintenance" | "broken";

export interface Equipment {
  id: UUID;
  name: string;
  category: string;
  subcategory: string;
  status: EquipmentStatus;
  quantity: number;
  location: Record<string, unknown>;
  availability: Record<string, unknown>[];
  specifications: Record<string, unknown>;
  maintenance: Record<string, unknown>;
  maintenance_log: Record<string, unknown>[];
  license_required?: string | null;
  organization_id: UUID;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface VenueContact {
  name?: string | null;
  email?: string | null;
  phone?: string | null;
}

export interface Venue {
  name: string;
  address: string;
  capacity?: number | null;
  contact?: VenueContact | null;
}

export interface SoundRequirements {
  main_system?: string | null;
  monitors?: number | null;
  mixing_consoles: string[];
}

export interface LightingRequirements {
  moving_lights?: number | null;
  led_pars?: number | null;
  lighting_desks: string[];
}

export interface PowerRequirements {
  total_power_needed?: number | null;
  distros_required?: number | null;
}

export interface TechnicalRequirements {
  sound?: SoundRequirements | null;
  lighting?: LightingRequirements | null;
  power?: PowerRequirements | null;
}

export interface BudgetBreakdown {
  sound?: number | null;
  lighting?: number | null;
  video?: number | null;
  labor?: number | null;
  transport?: number | null;
}

export interface Budget {
  total: number;
  breakdown?: BudgetBreakdown | null;
}

export type EventStatus = "planning" | "confirmed" | "cancelled";

export interface EventCreate {
  name: string;
  description?: string | null;
  start_date: string;
  end_date: string;
  venue: Venue;
  technical_requirements?: TechnicalRequirements | null;
  budget?: Budget | null;
  status: EventStatus;
}

export interface Event {
  id: UUID;
  name: string;
  description?: string | null;
  start_date: string;
  end_date: string;
  venue: Venue;
  technical_requirements: TechnicalRequirements;
  budget: Budget;
  status: EventStatus;
  created_by: UUID;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface Token {
  access_token: string;
  token_type: string;
}
