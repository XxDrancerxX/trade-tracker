// filepath: frontend/src/apiClient.test.js
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { apiFetch } from "../apiClient.js";
//------------------------------------------------------------------------------------------------------------------------------
// Import:	    Purpose
// describe:	Groups related tests together (like a folder)
// it:	        Defines a single test case (alias for test())
// expect:	    Makes assertions (expect(x).toBe(y))
// vi:	        Vitest's mocking utility (like Jest's jest)
// beforeEach:	Runs setup code before each test
// afterEach:	Runs cleanup code after each test
// apiFetch:	The actual function we're testing
//------------------------------------------------------------------------------------------------------------------------------

// Creates a fake Response object that mimics what the browser's fetch() returns.
function makeJsonResponse(body, status = 200) {
  return {
    ok: status >= 200 && status < 300, //it will return true or false based on the status code.
    status, // returns the HTTP status code provided (default 200)
    headers: {
      get(name) { // Simulates response.headers.get('Content-Type')
        if (name.toLowerCase() === "content-type") {
          return "application/json";
        }
        return null;
      },
    },
    json: async () => body, // Simulates response.json() to return the provided body
    text: async () => JSON.stringify(body), // Simulates response.text() to return stringified body
  };
}
//------------------------------------------------------------------------------------------------------------------------------

// Test suite for apiFetch function
// Groups all tests related to apiFetch together
describe("apiFetch", () => {   
  beforeEach(() => {  
    global.fetch = vi.fn()
    // vi.fn() - Creates a spy function (records all calls)    
    // global.fetch = - Replaces the real fetch() with our mock
  });
 

  afterEach(() => {   // ==>> Cleans up after each test AND Clears call history so next test starts fresh
    ////runs after every test in the describe() block.
    //Clearing call history (.mock.calls = [])
  
    vi.resetAllMocks();
   
  });
     
    //--------------------------------------------------------------------------------------------------------------------------------
    // Defines one test case
    // async because apiFetch returns a Promise 
  it("sends JSON body and sets credentials=include by default", async () => {
    const payload = { hello: "world" };
    // We call apiFetch() with:
    // Path: /api/test
    // Options: { method: "POST", body: { hello: "world" } }    

    global.fetch.mockResolvedValue(makeJsonResponse({ ok: true })); // Mock fetch to return a successful response
    // apiFetch() will call fetch() internally, so we need to mock it first.
    //mockResolvedValue() - Tells the spy to return a resolved Promise with our fake response when called.

    const result = await apiFetch("/api/test", {
      method: "POST",
      body: payload,
    });

    // 1) Result should be parsed JSON
    expect(result).toEqual({ ok: true });

    // 2) fetch should have been called exactly once
    expect(global.fetch).toHaveBeenCalledTimes(1);

    // 3) Inspect how fetch was called
    //	Gets arguments from the first call to the spy
    // When we create a spy with vi.fn(), Vitest automatically tracks every call to that function in a special array called mock.calls.
    const [url, options] = global.fetch.mock.calls[0];

    // URL should include the path
    expect(url).toContain("/api/test");

    // Credentials should default to "include"
    expect(options.credentials).toBe("include");

    // Content-Type should be JSON
    expect(options.headers["Content-Type"]).toBe("application/json");

    // Body should be stringified JSON
    expect(options.body).toBe(JSON.stringify(payload));
    // expect().toEqual()	Checks if values are deeply equal
    // expect().toBe()	Checks if values are identical (same reference)
  });

  //-------------------------------------------------------------------------------------------------------------------------------
  // This test verifies that our apiFetch function automatically handles expired access tokens by refreshing them and retrying the original request.

  it("on 401 once, calls /auth/token/refresh then retries original request", async () => {
    // Call 1: original request → 401 Unauthorized
    global.fetch
      .mockResolvedValueOnce(
        makeJsonResponse({ detail: "Unauthorized" }, 401)
      )
      // Call 2: refresh endpoint → 200 OK
      .mockResolvedValueOnce(
        makeJsonResponse({ ok: true }, 200)
      )
      // Call 3: retried original request → 200 OK with data
      .mockResolvedValueOnce(
        makeJsonResponse({ user: "alice" }, 200)
      );
      //mockResolvedValueOnce() - Tells the spy to return a resolved Promise with our fake response for each call in sequence.
      //makeJsonResponse() - Helper function to create a mock Response object with JSON data.

    const result = await apiFetch("/api/me/");

    // Final result should be the successful retry response
    expect(result).toEqual({ user: "alice" });

    // 3 calls total: original, refresh, retry
    expect(global.fetch).toHaveBeenCalledTimes(3);

    const [firstUrl] = global.fetch.mock.calls[0];
    const [secondUrl] = global.fetch.mock.calls[1];
    const [thirdUrl] = global.fetch.mock.calls[2];

    // First and third calls are the same endpoint (/api/me/)
    expect(firstUrl).toContain("/api/me/");
    expect(thirdUrl).toContain("/api/me/");

    // Second call should hit the refresh endpoint
    expect(secondUrl).toContain("/api/auth/token/refresh/");
  });


  //-------------------------------------------------------------------------------------------------------------------------------
  // This test verifies that if the refresh token request also fails, our apiFetch function throws an error with code AUTH_EXPIRED.

  it("if refresh also fails, throws error with code AUTH_EXPIRED", async () => {
    // Call 1: original request → 401
    // Call 2: refresh endpoint → 401 again (refresh fails)
    global.fetch
      .mockResolvedValueOnce(
        makeJsonResponse({ detail: "Unauthorized" }, 401)
      )
      .mockResolvedValueOnce(
        makeJsonResponse({ detail: "Refresh failed" }, 401)
      );

    let caught = null;
    try {
      await apiFetch("/api/me/");
    } catch (err) {
      caught = err;
    }

    expect(caught).toBeTruthy();
    expect(caught.status).toBe(401);
    expect(caught.code).toBe("AUTH_EXPIRED");
    // Optional: body from refresh error
    expect(caught.body).toEqual({ detail: "Refresh failed" });

    // Only 2 calls: original + refresh (no retry because refresh failed)
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });
});
