from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any


class GamePhase(Enum):
    SETUP = "setup"           # Mulligan, colocar carta al fondo, retornar cartas de tesoro y de combate
    MAIN_1 = "main_1"         # Fase principal antes del combate
    ATTACK = "attack"         # Declarar atacantes y defensores
    MAIN_2 = "main_2"         # Fase principal después del combate
    END = "end"               # Fin de turno


@dataclass
class ActionResult:
    success: bool
    message: str
    data: Optional[Any] = None


class ActionType(Enum):
    PLAY_CARD = "play_card"
    ATTACK = "attack"
    DEFEND = "defend"
    ACTIVATE_ABILITY = "activate_ability"
    PASS_PHASE = "pass_phase"
    MULLIGAN_RETURN = 'mulligan_return'



class GameState:
    def __init__(self, player1, player2):
        # Estado del juego
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.current_phase = GamePhase.SETUP
        self.turn_number = 1
        self.game_over = False
        self.winner = None
        
        # Estado de combate
        self.declared_attackers = []
        self.declared_defenders = {}  # {atacante: defensor}
        self.combat_resolved = False
        
        # Control de fases
        self.waiting_for_action = None  # Qué acción esperamos
        self.players_pending = []       # Qué jugadores deben actuar
        self.phase_actions_taken = []  # Track de acciones en la fase actual
        
        
    def advance_phase(self):
        """Avanza a la siguiente fase"""
        self._end_current_phase()
        
        if self.current_phase == GamePhase.SETUP:
            self.current_phase = GamePhase.MAIN_1
        elif self.current_phase == GamePhase.MAIN_1:
            self.current_phase = GamePhase.ATTACK
        elif self.current_phase == GamePhase.ATTACK:
            self.current_phase = GamePhase.MAIN_2
        elif self.current_phase == GamePhase.MAIN_2:
            self.current_phase = GamePhase.END
        elif self.current_phase == GamePhase.END:
            self.current_phase = GamePhase.SETUP
            
        self._start_current_phase()
            
    
    def _start_current_phase(self):
        """ Acciones automáticas al empezar una fase """
        if self.current_phase == GamePhase.SETUP:
            self._setup_turn()
        elif self.current_phase == GamePhase.MAIN_1:
            self._main_turn()
        elif self.current_phase == GamePhase.ATTACK:
            self._attack_turn()
        
        # Limpiar acciones de fase anterior
        self.phase_actions_taken.clear()
        
        
    def can_play_card(self, player, card_id):
        """Valida si se puede jugar una carta en la fase actual"""
        
    def can_attack(self, player, card_id):
        """Valida si se puede atacar con una carta"""
        
    def can_defend(self, player, attacker_id, defender_id):
        """Valida si se puede defender un ataque"""
        
    def _execute_play_card(self):
        pass
    
    
    def _execute_attack(self):
        pass
    
    
        
    def execute_action(self, player, action_type, **kwargs):
        """Ejecuta una acción si es válida en la fase actual"""
        valid_actions = {
            GamePhase.SETUP: [ActionType.PASS_PHASE, ActionType.MULLIGAN_RETURN],
            GamePhase.MAIN_1: [ActionType.PLAY_CARD, ActionType.ACTIVATE_ABILITY, ActionType.PASS_PHASE],
            GamePhase.ATTACK: [ActionType.ATTACK, ActionType.DEFEND, ActionType.PASS_PHASE],
            GamePhase.MAIN_2: [ActionType.PLAY_CARD, ActionType.ACTIVATE_ABILITY, ActionType.PASS_PHASE],
            GamePhase.END: [ActionType.PASS_PHASE]
        }
        
        # Verificar si la acción es válida en la fase actual
        if action_type not in valid_actions[self.current_phase]:
            return ActionResult(False, f"No puedes {action_type.value} en la fase {self.current_phase.value}")
        
        if self.waiting_for_action == "mulligan_return":
            return self._handle_mulligan_return(player, kwargs.get('card_id'))
        
        # Ejecutar la acción específica
        if action_type == ActionType.PLAY_CARD:
            return self._execute_play_card(player, kwargs.get('card_id'))
        elif action_type == ActionType.ATTACK:
            return self._execute_attack(player, kwargs.get('attacker_id'))
        elif action_type == ActionType.PASS_PHASE:
            self.advance_phase()
            return ActionResult(True, f"Avanzando a {self.current_phase.value}")
        
        return ActionResult(False, "Acción no implementada")
    
    
    def check_win_conditions(self):
        """Verifica condiciones de victoria"""
        
    def get_valid_actions(self, player):
        """Retorna las acciones válidas para el jugador en la fase actual"""
        
    def _resolve_combat(self):
        pass
    
    def _cleanup_phase(self):
        pass
    
    def _setup_turn(self):
        """ Acciones automáticas al comenzar fase SETUP """
        # 
        if self.turn_number == 1:
            self.player1.actions.draw_card(7)
            self.player2.actions.draw_card(7)
            self.waiting_for_action = "mulligan_return"
            self.players_pending = [self.player1, self.player2]
            
    
    def _main_turn(self):
        """ Acciones automáticas al comenzar fase MAIN """
        pass
    
    def _attack_turn(self):
        """ Acciones automáticas al comenzar fase ATTACK """
        pass
        
    def _end_current_phase(self):
        """ Acciones automáticas al terminar una fase """
        if self.current_phase == GamePhase.ATTACK:
            self._resolve_combat()
        elif self.current_phase == GamePhase.END:
            self._cleanup_phase()
    
    def _end_turn(self):
        """ Acciones automáticas al terminar una fase """
        self.waiting_for_action = None
        self.players_pending = []
        self.phase_actions_taken = []

    def _handle_mulligan_return(self, player, card_id):
        if player not in self.players_pending:
            return ActionResult(False, "No es tu turno")
        
        if card_id and not player.zones.hand.get_card_by_id(card_id):
            return ActionResult(False, "Carta no encontrada")
        
        if player.mulligan and not card_id:
            return ActionResult(False, "Seleccionar Carta")
        
        if card_id:
            player.actions.first_turn_return_card_to_bottom(card_id)
            self.players_pending.remove(player)
            if not self.players_pending:
                self.waiting_for_action = None
                self.advance_phase()
                return ActionResult(True, "Todas las cartas retornadas al mazo")
        
        else:
            player.actions.mulligan()
            player.mulligan = True
            
        