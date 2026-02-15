# Battleship Game

A classic Battleship game with an intelligent AI opponent using hunt/target algorithm.
# 🛳️ Battleship AI (Hunt–Target Strategy)

## How to Play
An intelligent Battleship AI implemented in Python using a **Hunt–Target strategy**, enhanced with **graph traversal (DFS)** and **probability-based scoring** for efficient ship detection and elimination.

1. **Ship Placement Phase**: 
   - Select a ship
   - Toggle orientation (Horizontal/Vertical)
   - Click on your grid to place the ship
   - Place all 5 ships to start the game
This AI is designed to play optimally on a standard Battleship board by switching between exploration and focused destruction once a ship is found.

2. **Battle Phase**:
   - Click on the enemy grid to attack
   - Computer will respond with its own attack
   - Sink all enemy ships to win!

## Features
 ✨ Features

* 🔍 **Hunt Mode**

  * Uses probability scoring to find the most likely ship locations
  * Dynamically adapts based on remaining ship sizes
  * Avoids already tried or invalid cells

* 🎯 **Target Mode**

  * Activates when a HIT is found
  * Uses DFS to group connected HIT cells into components
  * Determines ship orientation (horizontal / vertical)
  * Greedily extends hits until the ship is boxed in (assumed sunk)

* 🧠 **Graph-Based Reasoning**

  * Models HIT cells as a graph
  * Uses connected components to track partially destroyed ships

* ⚡ **Efficient & Practical**

  * Worst-case complexity: `O(N²)`
  * Practically constant time for standard 10×10 boards

---

## 📂 Project Structure

```
.
├── battleship_ai.py      # Main AI logic
├── board.py              # Board constants and state
├── graph.py              # GridGraph and Vertex classes
└── README.md             # Project documentation
```

---

## 🧠 How the AI Works

### 1️⃣ Hunt Mode (Search Phase)

* AI scans the board using a **probability grid**
* Each empty cell is scored based on how many ship placements include it
* Chooses the highest-scoring cell (bucket sort for efficiency)

Used when:

* No active ship is being targeted

---

### 2️⃣ Target Mode (Destroy Phase)

Triggered after a **HIT**.

#### Steps:

1. **Find hit components**

   * DFS groups adjacent HIT cells into connected components
2. **Lock onto a component**

   * The AI focuses on one suspected ship at a time
3. **Discovery Phase**

   * If only one HIT exists, probe its neighbors
4. **Commit Phase**

   * Determine ship orientation (horizontal or vertical)
5. **Extension Phase**

   * Extend hits from both ends until blocked
6. **Release Phase**

   * If both ends are blocked, assume ship is sunk
   * Reset back to Hunt Mode

---

## 🧩 Key Concepts

### `target_hits`

Stores the **currently active HIT component** representing a ship that is believed to still be alive.

### `hit_components`

Computed fresh each turn from the board using DFS.
Each component represents a contiguous cluster of HIT cells.

### Heuristic Sinking

Ships are considered sunk when:

* Both ends are blocked by MISS or board edges
  (No explicit SUNK marking is used.)

---

## ⏱️ Time Complexity

| Operation               | Complexity         |
| ----------------------- | ------------------ |
| Hit component detection | `O(N²)`            |
| Target extension        | `O(1)`             |
| Hunt scoring            | `O(N² × ship_len)` |
| Overall (practical)     |   O(N²)            |

> With standard Battleship constraints (10×10 board, max ship size 5), the AI is extremely fast.

---

## 🧪 Usage


The AI is designed to integrate cleanly with an external Battleship game engine.

- Interactive web-based UI
- Intelligent AI using hunt/target algorithm with parity-based hunting
- Real-time game state updates
- Visual feedback for hits, misses, and sunk ships
- Fleet status tracking