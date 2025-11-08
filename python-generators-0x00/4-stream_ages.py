"""
4-stream_ages.py - Stream user ages from database using a generator

CONCEPT: Streaming Specific Data
=================================
Instead of fetching entire user objects, we can stream just the data we need.
This is even MORE memory efficient!

Full user object: {user_id, name, email, age} = ~200 bytes
Just age: 25.50 = ~8 bytes

For 1 million users:
- Full objects: ~200 MB in memory
- Just ages: ~8 MB in memory
That's 25x less memory!"""