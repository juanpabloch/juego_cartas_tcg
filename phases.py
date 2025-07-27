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
    USE_TREASURE = "use_treasure"
    ATTACK = "attack"
    DEFEND = "defend"
    ACTIVATE_ABILITY = "activate_ability"
    PASS_PHASE = "pass_phase"
    RETURN = 'return'
    MULLIGAN = 'mulligan'



class GameState:
    def __init__(self, player1, player2):
        # Estado del juego
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.priority_player = player1
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
        
        print(f">>> AVANZANDO DE {self.current_phase.value} A...", end=" ")
        # self._end_current_phase()
        self.waiting_for_action = None
        self.players_pending.clear()
        
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
        
        print(f"{self.current_phase.value.upper()}")
        
        if self.current_phase != GamePhase.END:
            self._start_current_phase()
        else:
            self._end_turn()
            self.advance_phase()

    
    
    def _start_current_phase(self):
        """ Acciones automáticas al empezar una fase """
        
        print(f"=== INICIANDO FASE: {self.current_phase.value.upper()} ===")
        print(f"Jugador activo: {self.current_player.name}")
        print(f"Turno: {self.turn_number}")
        
        if self.current_phase == GamePhase.SETUP:
            self._setup_turn()
        elif self.current_phase == GamePhase.MAIN_1:
            self._main_turn()
        elif self.current_phase == GamePhase.ATTACK:
            self._attack_turn()
        elif self.current_phase == GamePhase.MAIN_2:
            self._main_turn()
        elif self.current_phase == GamePhase.END:
            self._end_turn()
        
    
    # def _end_current_phase(self):
    #     """ Acciones automáticas al terminar una fase """
    #     if self.current_phase == GamePhase.SETUP:
    #         pass
    #     elif self.current_phase == GamePhase.MAIN_1:
    #         pass
    #     elif self.current_phase == GamePhase.ATTACK:
    #         self._resolve_combat()
    #     elif self.current_phase == GamePhase.MAIN_2:
    #         pass
    #     elif self.current_phase == GamePhase.END:
    #         # self._cleanup_phase()
    #         self.player1.zones.clean_turn()
    #         self.player2.zones.clean_turn()
            
    
    
    def _setup_turn(self):
        """ Acciones automáticas al comenzar fase SETUP """
        # 
        if not self.players_pending:
            self.set_pending_players()
            
        if self.turn_number == 1:
            if not self.waiting_for_action:
                print(">>> Robando cartas iniciales...")
                self.player1.actions.draw_card_from_mazo(7)
                self.player2.actions.draw_card_from_mazo(7)
                
                self.player2.actions.get_token()
                
                self.waiting_for_action = "mulligan_return"
            
            return
            
        self.waiting_for_action = "setup_phase"
    
    
    def _main_turn(self):
        """ Acciones automáticas al comenzar fase MAIN """
        if not self.players_pending:
            self.set_pending_players()
            
        if not self.waiting_for_action:
            self.waiting_for_action = "main_phase"
    
    
    def _attack_turn(self):
        """ Acciones automáticas al comenzar fase ATTACK """
        if not self.players_pending:
            self.set_pending_players()

        if not self.waiting_for_action:
            self.waiting_for_action = "attack_pase"
        
    
    def _end_turn(self):
        """ Acciones automáticas al terminar un turno """
        print(">>> Limpiando turno...")
        # retornamos las cartas
        self.player1.zones.clean_turn()
        self.player2.zones.clean_turn()
        
        self.turn_number += 1
        self.priority_player = self.player2 if self.priority_player == self.player1 else self.player1
        self.current_player = self.priority_player
        
        print(f">>> Nuevo turno: {self.turn_number}, jugador: {self.current_player.name}")
        
        
    def get_oponent(self):
        """Obtiene el oponente del jugador actual"""
        return self.player2 if self.current_player == self.player1 else self.player1
    
    
    def set_pending_players(self):
        """Establece el orden de jugadores pendientes"""
        if self.priority_player == self.player1:
            self.players_pending = [self.player1, self.player2]
        else:
            self.players_pending = [self.player2, self.player1]

    
    def execute_action(self, player, action_type, **kwargs):
        """Ejecuta una acción si es válida en la fase actual"""
        print(f">>> {player.name} intenta: {action_type.value}")
        
        valid_actions = {
            GamePhase.SETUP: [ActionType.PASS_PHASE, ActionType.MULLIGAN, ActionType.RETURN],
            GamePhase.MAIN_1: [ActionType.PLAY_CARD, ActionType.ACTIVATE_ABILITY, ActionType.USE_TREASURE, ActionType.PASS_PHASE],
            GamePhase.ATTACK: [ActionType.ATTACK, ActionType.DEFEND, ActionType.PASS_PHASE],
            GamePhase.MAIN_2: [ActionType.PLAY_CARD, ActionType.ACTIVATE_ABILITY, ActionType.USE_TREASURE, ActionType.PASS_PHASE],
            GamePhase.END: [ActionType.PASS_PHASE]
        }
        
        # Verificar si la acción es válida en la fase actual
        if action_type not in valid_actions[self.current_phase]:
            return ActionResult(False, f"No puedes {action_type.value} en la fase {self.current_phase.value}")
        
        # Ejecutar la acción específica
        if action_type == ActionType.MULLIGAN:
            if player.zones.hand.mulligan_used:
                return ActionResult(False, "Ya hiciste mulligan")
            
            player.actions.mulligan()
            player.actions.draw_card_from_mazo(7)
            return ActionResult(True, "Mulligan realizado")
        
        if action_type == ActionType.RETURN:
            card_id = kwargs.get('card_id')
            if not card_id:
                return ActionResult(False, "Debes especificar una carta")
            
            if not player.zones.hand.get_card_info_by_id(card_id):
                return ActionResult(False, "Carta no encontrada")
            
            result = player.actions.first_turn_return_card_to_bottom(card_id)
            if result:
                return ActionResult(True, "Carta enviada al fondo del mazo")
            else:
                return ActionResult(False, "Error al enviar carta")
        
        elif action_type == ActionType.PLAY_CARD:
            # return self._execute_play_card(player, kwargs.get('card_id'))
            return player.actions.play_card_from_hand(kwargs.get('card_id'))
        
        elif action_type == ActionType.USE_TREASURE:
            return player.actions.agotar_tesoro(kwargs.get('card_id'))
        
        elif action_type == ActionType.ATTACK:
            return self._execute_attack(player, kwargs.get('attacker_id'))
        
        elif action_type == ActionType.PASS_PHASE:
            if player not in self.players_pending:
                return ActionResult(False, "No es tu turno para pasar")
            
            self.players_pending.remove(player)
            print(f">>> {player.name} pasa la fase")
            print(f"Jugadores restantes: {[p.name for p in self.players_pending]}")
            
            if not self.players_pending:
                print(">>> Todos los jugadores pasaron, avanzando fase...")
                self.current_player = self.priority_player
                self.advance_phase()

            else:
                self.current_player = self.players_pending[0]
                print(f">>> Turno de: {self.current_player.name}")
                return ActionResult(True, f"{player.name} pasó - Continúa {self.current_player.name}")
        
        return ActionResult(False, "Acción no implementada")
    

    def _handle_mulligan_return(self):
        """Maneja la fase de mulligan/return de cartas"""
        if not self.players_pending:
            # Terminar mulligan
            self.advance_phase()
        
        player = self.players_pending[0]
        
        print(f"\n=== MULLIGAN - {player.name} ===")
        print("CARTAS EN MANO:")
        for i, card in enumerate(player.zones.hand.see_cards(), 1):
            print(f"{i}. {card.name} (ID: {card.instance_id}) - Costo: {card.cost}")
        
        print("\nOPCIONES:")
        if not player.zones.hand.mulligan_used:
            print("1: Hacer mulligan (descartar toda la mano)")
        print("2: Mantener mano y devolver 1 carta al mazo")
        
        try:
            option = int(player.get_player_input("Selecciona opción"))
            
            if option == 1 and not player.zones.hand.mulligan_used:
                result = self.execute_action(player, ActionType.MULLIGAN)
                print(f">>> {result.message}")
                return result
                
            elif option == 2:
                card_id = player.get_player_input("ID de la carta a devolver")
                result = self.execute_action(player, ActionType.RETURN, card_id=card_id)
                
                if result.success:
                    self.players_pending.remove(player)
                    print(f">>> {result.message}")
                    
                    if not self.players_pending:
                        self.waiting_for_action = None
                        self.advance_phase()
                
                return result
            else:
                return ActionResult(False, "Opción no válida")
                
        except ValueError:
            return ActionResult(False, "Entrada inválida")

    
    def _handle_setup_turn(self):
        """Maneja la fase setup de cartas"""
        if not self.players_pending:
            self.advance_phase()
            
        player = self.players_pending[0]
            
        print(f"\n=== SETUP - {player.name} ===")
        card_result = player.actions.draw_card_from_mazo()
        if not card_result:
            print("MANO LLENA")
        treasure_result = player.actions.draw_treasure()
        if not treasure_result:
            print("TESOROS LLENO")

        self.players_pending.remove(player)
        
        if not self.players_pending:
            self.waiting_for_action = None
            self.advance_phase()
            
    
    def _handle_play_card(self):
        if not self.players_pending:
            self.advance_phase()
        
        player = self.players_pending[0]
        
        print(f"\n=== JUGAR CARTA - {player.name} ===")
        print("CARTAS EN MANO:")
        for i, card in enumerate(player.zones.hand.see_cards(), 1):
            print(f"{i}. {card.name} (ID: {card.instance_id}) - Costo: {card.cost}")
        
        print("\n")
        card_id = player.get_player_input("Selecciona una carta")
        result = self.execute_action(player, ActionType.PLAY_CARD, card_id=card_id)
        if result:
            return ActionResult(True, "Carta jugada")
        return ActionResult(False, "No se puede jugar Carta")
    
    
    def _handle_use_treasure(self):
        if not self.players_pending:
            self.advance_phase()

        player = self.players_pending[0]
        
        print(f"\n=== AGOTAR TESORO - {player.name} ===")
        print("TESOROS EN JUEGO:")
        for i, card in enumerate(player.zones.reserva_tesoros.see_cards(), 1):
            print(f"{i}. {card.name} (ID: {card.instance_id}) - Costo: {card.cost}")
        
        print("\n")
        card_id = player.get_player_input("Selecciona una carta")
        result = self.execute_action(player, ActionType.USE_TREASURE, card_id=card_id)
        if result:
            return ActionResult(True, "Tesoro agotado")
        return ActionResult(False, "No se puede jugar Carta")
    
    
    def pass_phase(self):
        return self.execute_action(self.current_player, ActionType.PASS_PHASE)

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
    
    def check_win_conditions(self):
        """Verifica condiciones de victoria"""
        
    def get_valid_actions(self, player):
        """Retorna las acciones válidas para el jugador en la fase actual"""
        
    def _resolve_combat(self):
        pass

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