# pwgenService
Rest API that genrates secure passwords (as long as you specify a good set of parameters)

Get passwords by sending GET requests to `/api/v1/password` and include these parameters:

- `length` - the length of the password(s) to generate
- `specials` - the number of special characters in the password
- `numbers` - the number of values the password should include
- `count` - How many characters should be generated

Example: `/api/v1/password?length=14&specials=2&numbers=2&count=5`

The generated passwords are returned as a list in JSON format.