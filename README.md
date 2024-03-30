
# Table Of Contents
- [Table Of Contents](#table-of-contents)
- [Important Note](#important-note)
- [The Intent](#the-intent)
- [Future Plans](#future-plans)
  - [Engine Expansion](#engine-expansion)
  - [Multiplayer](#multiplayer)

# Important Note
 This repository and codebase is heavily WIP. Do not rely on anything
 that you see here, and do not take it as any form of final product.

# The Intent
 Eclipse game engine is meant to make way for me to more
 easily create side-on tile-based games in future, without needing
 to constantly rewrite systems logic from the ground up.

 The project may eventually be expanded and built up in such
 a way that anyone can pick it up and develop their game on top of it,
 but at the moment it's designed as a starting point for my own games.

# Future Plans

## Engine Expansion
 The Eclipse engine will support entities, which are essentially
 glorified physics-based bounding rects.

 The engine will also support particle systems that can interact with
 the world visually, or "non destructively". Particles add a great
 layer to games, so without them Eclipse would be lacking that touch.

## Multiplayer
 Eclipse will ideally support multiplayer systems using hybrid
 TCP and UDP connections (UDP for non-important or fast-paced packets).