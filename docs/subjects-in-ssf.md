# Subjects in the Shared Signals Framework
Subjects are defined in detail in the
[Subject Identifiers for Security Event Tokens spec](https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers),
and the Shared Signals Framework adds [three new subject types](https://openid.net/specs/openid-sse-framework-1_0.html#subject-principals)
to that list.

Subject Identifiers are JSON objects and can either be
[Simple Subjects](https://openid.net/specs/openid-sse-framework-1_0.html#simple-subjects),
which have a format field and other claims specific to each subject type, or they can be
[Complex Subjects](https://openid.net/specs/openid-sse-framework-1_0.html#complex-subjects),
which have a number of claims, each of which maps to a Simple Subject.

For instance, here is a Simple Subject with the Email format:

```json5
{
    "format": "email",
    "email": "user@example.com"
}
```

  - `format`: [REQUIRED] A string that can be one of `account`, `aliases`, `did`, `email`, `iss_sub`, `jwt_id`, `opaque`, `phone_number`, or `saml_assertion_id`.
  - `email`: [REQUIRED for Email subject identifier] The email address of the subject.

The available Simple Subject types are:
  - [Account](https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.1)
  - [Aliases](https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.2)
  - [DID](https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.3)
  - [Email](https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.4)
  - [IssSub](https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.5)
  - [JwtID](https://openid.net/specs/openid-sse-framework-1_0.html#sub-id-jwt-id)
  - [Opaque](https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.6)
  - [PhoneNumber](https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.7)
  - [SamlAssertionID](https://openid.net/specs/openid-sse-framework-1_0.html#sub-id-saml-assertion-id)

And here is a Complex Subject that defines the user and tenant claims:
```json5
{
    "user": {
      "format": "email",
        "email": "user@example.com"
    },
    "tenant" : {
      "format": "iss_sub",
      "iss" : "http://example.com/idp1",
      "sub" : "1234"
    }
}
```

  - `user`: [OPTIONAL] A simple subject that identifies a user.
  - `tenant`: [OPTIONAL] A simple subject that identifies a tenant.

All Complex Subject claims are OPTIONAL, but at least one must be present. The available claims are:
  - application
  - device
  - group
  - org_unit
  - session
  - tenant
  - user
