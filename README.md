# ChessPython
A chess engine and user-interface that a player could play against.
  This code is very disorginized, but if you run Main.py a PyGame frame appears, and you can play against the computer.
  The computer is just a simple recursive formula. You can adjust how well it plays using Player.RECURSION_DEPTH, 
although if you play it at anything higher than RECURSION_DEPTH = 2 it will be increadibly slow.
  The Engine is reponsible for managing the board. Its most difficult tasks are to calculate every possible move each turn,
when the game should end, and keep a record of the moves so the player can undo turns (using the LEFT key).
  Main is responsible for implementing the Engine, and all the user-interface related tasks. I used PyGame to for the UI.
