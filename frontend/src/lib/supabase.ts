import { createClient } from "@supabase/supabase-js"
import { env } from "./env"

export const supabase = createClient(env.supabaseUrl, env.supabaseAnonKey, {
  auth: {
    storage: sessionStorage, // clears as soon as the browser tab/window closes
    persistSession: true,
  },
})
