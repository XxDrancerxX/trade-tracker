//frontend/src/apiClient.js
//This is our gateway to interact with the backend API. It makes HTTP calls consistent, safe, and easy to change in one place.
//apiFetch normalizes headers, conditionally sets Content-Type, auto-stringifies plain objects, adds Authorization when needed,
//throws on non-ok responses (including parsed error body), and returns parsed JSON or text for successful responses.// filepath: /workspaces/trade-tracker/frontend/src/apiClient.js
import { API_URL } from "./config";
/**
 * apiFetch(path, options?)
 *
 * - Prefixes API_URL.
 * - Sends credentials (cookies).
 * - Auto JSON-stringifies plain objects if no Content-Type set.
 * - Parses JSON responses; throws on non-2xx with { status, body }.
 */

export async function apiFetch(path, options = {}) {
  // path is the endpoint path (e.g., "/trades")
  // options is the fetch options (method, headers, body, etc.)


  // Work on a shallow copy so we don't mutate caller's object
  const opts = { ...options }; // let the function modify opts freely before passing to fetch.

  // Normalize headers: support plain object or Headers instance
  // convert whatever the caller passed as options.headers into a plain JavaScript object so the helper can inspect, merge and modify header keys easily.
  const headersFromOptions =
    opts.headers instanceof Headers //hecks if opts.headers is an instance of the Headers class (the built-in Fetch API Headers object), not just whether a property named headers exists.
      ? Object.fromEntries(opts.headers.entries()) //if Headers instance, convert to plain object
      : (opts.headers || {}); //else use as-is or default to empty object

  // Case-insensitive check for Content-Type presence from caller
  const hasContentType = Object.keys(headersFromOptions).some( // Gets all header keys and checks if any match "content-type" case-insensitively.
    (k) => k.toLowerCase() === "content-type"
  );

  // Detect FormData / URLSearchParams / Blob / ArrayBuffer etc.
  // FormData and URLSearchParams have their own content types and should not be JSON-stringified.
  // The left side is evaluated first. If FormData doesn’t exist, the left side is false and the right side (instanceof) is never evaluated.
  // Only when FormData exists does it check opts.body instanceof FormData.
  const isFormData = typeof FormData !== "undefined" && opts.body instanceof FormData; // Checks if FormData is defined (browser environment) and if opts.body is an instance of FormData.
  const isUrlSearchParams = typeof URLSearchParams !== "undefined" && opts.body instanceof URLSearchParams; // Similar check for URLSearchParams.
  const isBinary = //Sets isBinary to true if opts.body is a Blob, ArrayBuffer, or Uint8Array.
    opts.body instanceof Blob ||
    opts.body instanceof ArrayBuffer ||
    opts.body instanceof Uint8Array;
        // Blob: binary data blob (File extends Blob). Good for uploads: images, PDFs, etc.
        // ArrayBuffer: raw fixed-length binary buffer.
        // Uint8Array: typed array view over an ArrayBuffer (Node.js Buffer extends Uint8Array, so this will be true for Buffer too).

  // Decide if we should auto-stringify the body to JSON
  const shouldStringify = // If body is a non-null object and not FormData, URLSearchParams, or binary, we should stringify it.
  // It will set true only when:
    opts.body != null &&
    typeof opts.body === "object" &&
    !isFormData &&
    !isUrlSearchParams &&
    !isBinary;

  // Start with caller headers (caller can override defaults)
  const headers = { ...headersFromOptions };


  // Only set Content-Type when we are sending JSON and caller didn't set it
  if (shouldStringify && !hasContentType) {
    headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(opts.body);
  }

  // Attach normalized headers to options passed to fetch
  opts.headers = headers;

  // Critical for cookie-based auth: always send cookies unless caller overrides.
  if (typeof opts.credentials === "undefined") {
    opts.credentials = "include";
  }

  const res = await fetch(`${API_URL}${path}`, opts); // Make the fetch call to the full URL

  // Attempt to parse error body and throw for non-ok responses
  const contentType = res.headers.get("content-type") || ""; // Get Content-Type header for response, default to empty string if missing
  if (!res.ok) {
    let errBody = null;
    try {
      if (contentType.includes("application/json")) { // If JSON, parse it
        errBody = await res.json(); // Try to parse error body as JSON
      } else { // Otherwise, get text
        errBody = await res.text(); // Try to get error body as text
      }
    } catch (e) {
      // ignore parse errors, keep errBody null
    }
    const err = new Error(`Request failed with status ${res.status}`);
    // attach additional info for callers
    err.status = res.status;
    err.body = errBody;
    throw err;
  }

  // Success: auto-parse JSON responses, return text for others, null for no-content
  if (res.status === 204 || res.status === 205) return null; // No Content or Reset Content
  if (contentType.includes("application/json")) return await res.json();
  return await res.text();
}
