# Page snapshot

```yaml
- generic [ref=e2]:
  - banner [ref=e3]:
    - text: Trade Tracker
    - link "Login" [ref=e4] [cursor=pointer]:
      - /url: /login
    - link "Signup" [ref=e5] [cursor=pointer]:
      - /url: /signup
  - generic [ref=e6]:
    - heading "Login" [level=1] [ref=e7]
    - paragraph [ref=e8]: Failed to fetch
    - paragraph [ref=e9]: Username and Password incorrect. Please try again.
    - generic [ref=e10]:
      - generic [ref=e12]:
        - text: Username
        - textbox "Username" [ref=e13]: superuser
      - generic [ref=e15]:
        - text: Password
        - textbox "Password" [ref=e16]: "123456"
      - button "Login" [ref=e17] [cursor=pointer]
```