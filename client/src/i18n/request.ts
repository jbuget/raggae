import { cookies } from "next/headers";
import { getRequestConfig } from "next-intl/server";

export const SUPPORTED_LOCALES = ["en", "fr"] as const;
export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];

export function isSupportedLocale(value: unknown): value is SupportedLocale {
  return SUPPORTED_LOCALES.includes(value as SupportedLocale);
}

const envLocale = process.env.DEFAULT_LOCALE;
export const DEFAULT_LOCALE: SupportedLocale = isSupportedLocale(envLocale) ? envLocale : "en";

export default getRequestConfig(async () => {
  const cookieStore = await cookies();
  const raw = cookieStore.get("raggae_locale")?.value;
  const locale: SupportedLocale = isSupportedLocale(raw) ? raw : DEFAULT_LOCALE;

  return {
    locale,
    messages: (await import(`../../messages/${locale}.json`)).default,
  };
});
