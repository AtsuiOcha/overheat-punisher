# 🔥 Overheat Detection Specification

## Overview
This document defines how the Overheat Punisher system detects "overheating" behavior in Valorant gameplay and triggers the chancla punishment mechanism.

---

## 🎯 Overheat Definition

### What is Overheating?
**Overheating occurs when a player takes an unnecessary fight while their team has a man advantage, resulting in death without getting traded out by teammates.**

### Specific Criteria:
1. **Man Advantage**: Your team has MORE alive players than the enemy team
2. **Player Death**: You die during this advantage state  
3. **No Trade**: No enemy dies within 3 seconds of your death
4. **Mid-Round Only**: Detection only occurs during active gameplay (not pre/post-round)

### Why This Matters:
- Throwing away team advantages loses rounds
- Unnecessary aggression when ahead is poor decision-making
- Creates accountability for tactical discipline

---

## 🔍 Detection Strategy

### Core Detection Pipeline:
```
Frame → Game State → Advantage Check → Death Event → Trade Window → Overheat Decision
```

### Required Detections:
1. **Round State**: Pre-round / Mid-round / Post-round
2. **Team Compositions**: Count alive players on both teams
3. **Player Death Events**: When YOU get eliminated
4. **Enemy Deaths**: Trade kills within time window
5. **Timer Information**: For precise 3-second trade window

### Detection Timing:
- **Sample Rate**: ~2-4 FPS (every 250-500ms)
- **Trade Window**: Exactly 3.0 seconds
- **History Retention**: 15 seconds of game states
- **Analysis Scope**: Current round only (reset between rounds)

---

## 🏗️ Architecture Plan

### Component Separation:
```
Main Driver ←→ Overheat Analyzer ←→ HUD Detection
     ↓
Hardware Trigger (Chancla)
```

### Main Driver Responsibilities:
- Frame capture and timing control
- Round lifecycle management  
- Hardware trigger coordination
- Performance monitoring

### Overheat Analyzer Responsibilities:
- Game state history tracking (15 seconds)
- Round state detection and filtering
- Overheat logic implementation
- Trade window management

### HUD Detection Enhancements:
- Add round state detection capability
- Optimize OCR reader reuse for performance
- Improve kill feed reliability

---

## 📊 Data Structures

### GameState:
```python
@dataclass
class GameState:
    timestamp: float           # Unix timestamp
    team1_alive: int          # Your team player count  
    team2_alive: int          # Enemy team player count
    player_dead: bool         # Your death status
    round_timer: int          # Seconds remaining
    round_state: RoundState   # PRE/MID/POST round
```

### Death Event Tracking:
```python
@dataclass  
class DeathEvent:
    death_timestamp: float    # When death occurred
    death_round_timer: int    # Round time when death occurred
    team1_count: int          # Your team count at death
    team2_count: int          # Enemy count at death
    had_advantage: bool       # Man advantage at death
```

---

## ⚡ Performance Optimizations

### Speed Requirements:
- **Target**: <100ms analysis time per frame
- **Valorant TTK**: ~150-300ms (system must be faster)
- **Trade Detection**: Must catch 3-second window reliably

### Optimization Strategies:
1. **Single-threaded design** for simplicity and speed
2. **OCR reader reuse** to avoid initialization overhead  
3. **Early exit conditions** during pre/post-round
4. **Minimal history retention** (15s sliding window)
5. **Time-based sampling** rather than every frame

### Memory Management:
- Rolling 15-second history buffer
- Automatic cleanup of old game states
- Reset state between rounds

---

## 🔄 Integration Flow

### Main Loop:
```python
analyzer = OverheatAnalyzer()

while game_running:
    if should_analyze_frame():  # Time-based sampling
        frame = capture_screen()
        
        if analyzer.process_frame(frame):
            trigger_chancla()
            log_overheat_event()
```

### Analyzer Interface:
```python
class OverheatAnalyzer:
    def process_frame(self, frame) -> bool:
        """Returns True if overheat detected"""
        
    def get_stats(self) -> dict:
        """Returns overheat statistics"""
        
    def reset_round(self):
        """Clears state for new round"""
```

---

## 🧪 Edge Cases & Exceptions

### Future Considerations:
- **Revive mechanics**: Handle Sage resurrections
- **Spike scenarios**: Post-plant positioning decisions  
- **Clutch situations**: 1vX scenarios might need different rules
- **Team coordination**: Voice comm context (future mic integration?)

### Error Handling:
- OCR failures fallback to previous state
- Network lag compensation
- Hardware trigger failures
- Round detection edge cases

---

## 🎯 Success Metrics

### Accuracy Goals:
- **False Positive Rate**: <5% (wrongful chancla slaps)
- **False Negative Rate**: <10% (missed overheats)
- **Response Time**: <500ms from death to decision
- **Detection Reliability**: >95% during clear gameplay

### Validation Methods:
- Manual review of recorded gameplay
- Statistical tracking over multiple matches
- Community feedback and tuning

---

## 🚀 Implementation Phases

### Phase 1: Core Detection
- Basic overheat detection with existing HUD functions
- Single-threaded main loop
- Simple hardware trigger

### Phase 2: Optimization  
- Performance tuning and OCR optimization
- Enhanced round state detection
- Reliability improvements

### Phase 3: Advanced Features
- Edge case handling
- Statistics dashboard
- Configuration interface

---

**¡La Chancla awaits your poor decisions! 🩴**