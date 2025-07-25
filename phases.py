from enum import Enum


class GamePhase(Enum):
    SETUP = "setup"           # Mulligan, colocar carta al fondo, retornar cartas de tesoro y de combate
    MAIN_1 = "main_1"         # Fase principal antes del combate
    ATTACK = "attack"         # Declarar atacantes y defensores
    MAIN_2 = "main_2"         # Fase principal después del combate
    END = "end"               # Fin de turno


class ActionResult:
    def __init__(self, success, message, data=None) -> None:
        self.success = success
        self.message = message
        self.data = data

    def __str__(self) -> str:
        return f"{self.success} | {self.message}"
    

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
        # self.priority_player = player1
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
            self.turn_number += 1
            
        self._start_current_phase()
            
    
    def _start_current_phase(self):
        """ Acciones automáticas al empezar una fase """
        if self.current_phase == GamePhase.SETUP:
            print("Start SETUP")
            self._setup_turn()
        elif self.current_phase == GamePhase.MAIN_1:
            print("Start MAIN 1")
            self._main_turn()
        elif self.current_phase == GamePhase.ATTACK:
            print("Start ATTACK")
            self._attack_turn()
        elif self.current_phase == GamePhase.MAIN_2:
            print("Start MAIN 2")
            self._main_turn()
        elif self.current_phase == GamePhase.END:
            print("Start END")
            self._end_turn()
            self.advance_phase()
        
        # # Limpiar acciones de fase anterior
        # self.phase_actions_taken.clear()
        # self.players_pending.clear()
        
        
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
        
        # Ejecutar la acción específica
        if action_type == ActionType.MULLIGAN_RETURN:
            return self._handle_mulligan_return(player, kwargs.get('card_id'))
        elif action_type == ActionType.PLAY_CARD:
            return self._execute_play_card(player, kwargs.get('card_id'))
        elif action_type == ActionType.ATTACK:
            return self._execute_attack(player, kwargs.get('attacker_id'))
        elif action_type == ActionType.PASS_PHASE:
            self.players_pending.remove(player)
            # aca puedo poner un condicional si los 2 jugadores pasan que avance la fase
            if not self.players_pending:
                self.advance_phase()
                return ActionResult(True, f"Avanzando a {self.current_phase.value}")
            self.current_player = self.players_pending[0]
            
        return ActionResult(False, "Acción no implementada")
    
    
    def check_win_conditions(self):
        """Verifica condiciones de victoria"""
        
        
    def get_valid_actions(self, player):
        """Retorna las acciones válidas para el jugador en la fase actual"""
        
        
    def _resolve_combat(self):
        pass
    
    
    def _cleanup_phase(self):
        self.player1.zones.retornar_tesoros_agotados()
        self.player1.zones.retornar_unidades_a_formacion()
        self.player2.zones.retornar_tesoros_agotados()
        self.player2.zones.retornar_unidades_a_formacion()
        self.current_player = self.get_oponent()
    
    
    def _setup_turn(self):
        """ Acciones automáticas al comenzar fase SETUP """
        # 
        if self.turn_number == 1 and not self.waiting_for_action:
            self.player1.actions.draw_card_from_mazo(7)
            self.player2.actions.draw_card_from_mazo(7)
            self.waiting_for_action = "mulligan_return"
            self.players_pending = [self.player1, self.player2]
            
    
    def _main_turn(self):
        """ Acciones automáticas al comenzar fase MAIN """
        self.players_pending = [self.player1, self.player2]
    
    
    def _attack_turn(self):
        """ Acciones automáticas al comenzar fase ATTACK """
        self.players_pending = [self.player1, self.player2]
        
        
    def _end_current_phase(self):
        """ Acciones automáticas al terminar una fase """
        if self.current_phase == GamePhase.ATTACK:
            self._resolve_combat()
        elif self.current_phase == GamePhase.END:
            self._cleanup_phase()
    
    
    def _end_turn(self):
        """ Acciones automáticas al terminar una fase """
        pass
        
    def get_oponent(self):
        if self.current_player == self.player1:
            return self.player2 
        return self.player1
    

    def _handle_mulligan_return(self, player, card_id):
        if player not in self.players_pending:
            return ActionResult(False, "No es tu turno")
        
        if card_id and not player.zones.hand.get_card_info_by_id(card_id):
            return ActionResult(False, "Carta no encontrada")
        
        if player.zones.hand.mulligan_used and not card_id:
            return ActionResult(False, "Seleccionar Carta")
        
        if card_id:
            result = player.actions.first_turn_return_card_to_bottom(card_id)
            if not result:
                return ActionResult(False, "Carta no se pudo enviar al mazo")
            
            self.players_pending.remove(player)
            if self.players_pending:
                return ActionResult(True, "Jugadores pendientes")
            
            self.player2.actions.get_token()
            self.waiting_for_action = None
            self.advance_phase()
            return ActionResult(True, "Cartas en el mazo")
            
        
        player.actions.mulligan()
        player.actions.draw_card_from_mazo(7)
        return ActionResult(True, "Mulligan realizado")


    def pass_phase(self):
        return self.execute_action(self.current_player, ActionType.PASS_PHASE)



# PHASE_ACTIONS = {
#     GamePhase.SETUP: {
#         'priority_player': [ActionType.MULLIGAN_RETURN, ActionType.PASS_PRIORITY],
#         'waiting_player': []  # No puede hacer nada
#     },
#     GamePhase.MAIN_1: {
#         'priority_player': [ActionType.PLAY_CARD, ActionType.ACTIVATE_ABILITY, ActionType.PASS_PRIORITY],
#         'other_player': [ActionType.FAST_ACTION, ActionType.ACTIVATE_ABILITY]  # Solo acciones rápidas
#     },
#     GamePhase.ATTACK: {
#         'active_player': [ActionType.DECLARE_ATTACKERS, ActionType.PASS_PRIORITY],
#         'defending_player': [ActionType.DECLARE_BLOCKERS, ActionType.FAST_ACTION]
#     }
# }
# 3. Validaciones Específicas
# Para cada acción, verificar:

# PLAY_CARD: ¿Tiene oro suficiente? ¿Es su turno? ¿Pila vacía?
# ATTACK: ¿Tiene unidades que pueden atacar? ¿Están en formación?
# ACTIVATE_ABILITY: ¿Puede pagar el coste? ¿Tiene prioridad?
# 4. Método de Implementación

# def get_valid_actions(self, player):
#     if player != self.priority_player:
#         return self._get_response_actions(player)  # Solo acciones rápidas
    
#     base_actions = PHASE_ACTIONS[self.current_phase]['priority_player']
#     return [action for action in base_actions if self._can_execute(player, action)]