# How to Create a Stream

The Shared Signals and Events spec leaves it up to the implementer how to
actually create an Event Stream. In order to help spread understanding, this
document will suggest some possible ways to create a stream. It is in no way an
authoritative or complete list.

An Event Stream is the conceptual mechanism by which a Transmitter sends security
events to a Receiver. If you have not yet read
[sharedsignals.guide](https://sharedsignals.guide),
which describes this process, we suggest you start there.

## What Info Needs to Be Shared?
In order for a Transmitter and Receiver to communicate securely, certain
information is needed by each party. Most of the configuration of the Event
Stream can be done via the Stream Management API, but there are a few pieces of
information that need to be shared out-of-band.

The Receiver has to know:
- Where to go to get the well-known configuration endpoints.
- A bearer token that can be used to authenticate its requests to the
Transmitter's Stream Management API.

The Transmitter has to know:
- The audience value to include in the "aud" claim of the event JWTs that it
sends to the Receiver.
- How to map the bearer token in the Stream Management API requests from the
Receiver to the correct stream.

## How Can This Info Be Shared?
There are numerous ways to create a stream and share this information. We will
detail two possible methods here: company-initiated and admin-initiated. In each
of the examples below, we assume that the bearer token that gets created to
identify the stream is a simple shared secret - like an API key. A more robust
solution might be to use 2-legged or 3-legged OAuth2 to create the bearer token,
but that is outside the scope of this document.

### Company Initiated
In [sharedsignals.guide](https://sharedsignals.guide) we introduce two imaginary
companies, PopularApp.com and MostSecure.com. There is a single stream connecting
these two companies that PopularApp listens on to receive notifications of their
users' accounts being compromised. In this hypothetical example, we can assume
that a partnership has been formed between the two companies. That is, we imagine
that folks from the two companies met, decided that they would like to have an
Event Stream connecting their services, and MostSecure securely shared some
randomly generated value for PopularApp to use as the bearer token. During that
meeting the other information described above was also relayed.

### Admin Initiated
Many security services are designed to protect workforce users. In this setting,
a business usually has one or more security admins who are responsible for making
sure the employees are using the company's equipment safely. That admin is a
trusted user who is allowed to make changes to policy and other settings on
behalf of the employees.

In this scenario, it would be reasonable for the transmitter company to offer a
UI in which the admin could enter the expected audience value and get back a
secret that could be used for the bearer token. This creates a stream on the
transmitter's side. The admin could then enter that secret value along with the
issuer value and well-known endpoints location into a UI at the receiver company,
connecting it to the stream from the receiver's side.

One benefit of this method is that it becomes easier to create per-tenant streams
between the companies, confining the failure domain of any particular stream to
the tenant involved.

## Creating a Stream with Our Example Code
While our example [transmitter](../examples/transmitter) and
[receiver](../examples/receiver) try to hew as close to the OpenID spec
as possible, we have also added a `/register` endpoint to the transmitter spec so
that a person who is experimenting with the demo can create a stream and test it
out. The endpoint takes an "audience" value and returns a token that can be used
as a bearer token.

In a real scenario, the `/register` endpoint might back a UI that an admin could
use to set up the stream. Our simplified example receiver uses this endpoint to
trigger the creation of a stream and connect to it on startup.
