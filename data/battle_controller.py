# coding=utf-8
import logging
import pickle

from typing import List, Dict
from copy import deepcopy

from replaydata import PlayerInfo, PlayerState

from replay_unpack.core import IBattleController
from replay_unpack.core.entity import Entity
from .constants import DamageStatsType, Category, TaskType, Status

try:
    from .constants import DEATH_TYPES
except ImportError:
    DEATH_TYPES = {}
from .players_info import PlayersInfo


class BattleController(IBattleController):

    def __init__(self):
        self._entities = {}
        self._achievements = {}
        self._ribbons = {}
        self._players = PlayersInfo()
        self._battle_result = None
        self._damage_map = {}
        self._shots_damage_map = {}
        self._death_map = []
        self._map = {}
        self._player_id = None
        self._arena_id = None
        self._dead_planes = {}

        ################################################################################################################
        self._time = 0
        self._previous_time = 0
        self._interval = 0.5
        self._playerInfo: List[PlayerInfo] = []
        self._playerStates: List[PlayerState] = []
        self._timedPlayerStates: Dict[int, List[PlayerState]] = {}
        self._caps_history = {}
        self.owner_team_id = 0
        ################################################################################################################

        Entity.subscribe_method_call('Avatar', 'onBattleEnd', self.onBattleEnd)
        Entity.subscribe_method_call('Avatar', 'onArenaStateReceived', self.onArenaStateReceived)
        Entity.subscribe_method_call('Avatar', 'onGameRoomStateChanged', self.onPlayerInfoUpdate)
        Entity.subscribe_method_call('Avatar', 'receiveVehicleDeath', self.receiveVehicleDeath)
        # Entity.subscribe_method_call('Vehicle', 'setConsumables', self.onSetConsumable)
        Entity.subscribe_method_call('Avatar', 'onRibbon', self.onRibbon)
        Entity.subscribe_method_call('Avatar', 'onAchievementEarned', self.onAchievementEarned)
        Entity.subscribe_method_call('Avatar', 'receiveDamageStat', self.receiveDamageStat)
        Entity.subscribe_method_call('Avatar', 'receive_planeDeath', self.receive_planeDeath)
        Entity.subscribe_method_call('Avatar', 'onNewPlayerSpawnedInBattle', self.onNewPlayerSpawnedInBattle)
        Entity.subscribe_method_call('Vehicle', 'receiveDamagesOnShip', self.g_receiveDamagesOnShip)
        Entity.subscribe_method_call('Avatar', 'updateMinimapVisionInfo', self.updateMinimapVisionInfo)
        Entity.subscribe_property_change('Vehicle', 'health', self.setHealth)
        Entity.subscribe_method_call('Avatar', 'receive_addMinimapSquadron', self.receive_addMinimapSquadron)

    ####################################################################################################################

    def update(self, time):
        self._time = time
        if time - self._previous_time >= self._interval:
            self._previous_time = time
            self._timedPlayerStates[time] = deepcopy(self._playerStates)

            caps = self._getCapturePointsInfo()
            self._caps_history[time] = deepcopy(caps)
            # print(caps)
            # print(str(time) + ': ' + str([cap['teamId'] for cap in caps]))

    def create_player_state_list(self):
        player: dict
        for _, player in self._players.get_info().items():
            pi = PlayerInfo()
            pi.id = player['id']
            pi.accountId = player['accountDBID']
            pi.avatarId = player['avatarId']
            pi.vehicleId = player['shipId']
            pi.nickname = player['name']
            pi.isOwner = self._player_id == player['avatarId']
            pi.maxHealth = player['maxHealth']
            pi.health = player['maxHealth']
            pi.shipParamsId = player['shipParamsId']
            pi.teamId = player['teamId']
            if self._player_id == player['avatarId']:
                self.owner_team_id = player['teamId']
            self._playerInfo.append(pi)

            ps = PlayerState()
            ps.id = player['id']
            ps.avatarId = player['avatarId']
            ps.vehicleId = player['shipId']
            self._playerStates.append(ps)

        for pi in self._playerInfo:
            pi.isAlly = self.owner_team_id == pi.teamId

    def update_player_state_list(self):
        for ps in self._playerStates:
            player = self._players.get_info()[ps.id]
            ps.isAlive = player['isAlive']
            ps.isAbuser = player['isAbuser']

    def updateMinimapVisionInfo(self, avatar, ships_minimap_diff, buildings_minimap_diff):
        pack_pattern = (
            (-2500.0, 2500.0, 11),
            (-2500.0, 2500.0, 11),
            (-3.141592753589793, 3.141592753589793, 9)
        )
        for e in ships_minimap_diff:
            vehicle_id = e['vehicleID']
            x, y, yaw = unpack_values(e['packedData'], pack_pattern)
            for ps in self._playerStates:
                if vehicle_id == ps.vehicleId:
                    ps.setPosition(x, y, yaw)
                    break

    def setHealth(self, vehicle, health):
        for ps in self._playerStates:
            if vehicle.id == ps.vehicleId:
                ps.health = health

    def receive_addMinimapSquadron(self, avatar, plane_id: int, team_id, gameparams_id, pos):
        packed = bin(plane_id)[2:]
        departures = int(packed[:1], 2)
        purpose = int(packed[1:4], 2)
        index = int(packed[4:7], 2)
        vehicle_id = int(packed[7:], 2)
        # print(departures, purpose, index, vehicle_id)

    ####################################################################################################################

    def onSetConsumable(self, vehicle, blob):
        print(pickle.loads(blob))

    @property
    def entities(self):
        return self._entities

    @property
    def battle_logic(self):
        return next(e for e in self._entities.values() if e.get_name() == 'BattleLogic')

    def create_entity(self, entity: Entity):
        self._entities[entity.id] = entity

    def destroy_entity(self, entity: Entity):
        self._entities.pop(entity.id)

    def on_player_enter_world(self, entity_id: int):
        self._player_id = entity_id

    def get_info(self):
        return dict(
            playerInfo=self._playerInfo,
            timedPlayerStates=self._timedPlayerStates,
            owner_team_id=self.owner_team_id,
            caps_history=self._caps_history,
            achievements=self._achievements,
            ribbons=self._ribbons,
            players=self._players.get_info(),
            battle_result=self._battle_result,
            damage_map=self._damage_map,
            shots_damage_map=self._shots_damage_map,
            death_map=self._death_map,
            death_info=self._getDeathsInfo(),
            map=self._map,
            player_id=self._player_id,
            control_points=self._getCapturePointsInfo(),
            tasks=list(self._getTasksInfo()),
            skills=dict(self._getCrewSkillsInfo()),
            # planes are only updated in AOI
            # so information is not right
            # planes=self._dead_planes,
            arena_id=self._arena_id
        )

    def _getDeathsInfo(self):
        deaths = {}
        for killedVehicleId, fraggerVehicleId, typeDeath in self._death_map:
            death_type = DEATH_TYPES.get(typeDeath)
            if death_type is None:
                logging.warning('Unknown death type %s', typeDeath)
                continue

            deaths[killedVehicleId] = {
                'killer_id': fraggerVehicleId,
                'icon': death_type['icon'],
                'name': death_type['name'],
            }
        return deaths

    def _getCapturePointsInfo(self):
        return self.battle_logic.properties['client']['state'].get('controlPoints', [])

    def _getTasksInfo(self):
        tasks = self.battle_logic.properties['client']['state'].get('tasks', [])
        for task in tasks:
            yield {
                "category": Category.names[task['category']],
                "status": Status.names[task['status']],
                "name": task['name'],
                "type": TaskType.names[task['type']]
            }

    def _get_learned_skills(self, vehicle):
        """
        Skill has his own skill id.
        Packed format = sum(2 ** skill_id for skill_id in skills)
        So to turn it back, we must divide number by two;
        """
        learned_skills = vehicle.properties['client']['crewModifiersCompactParams']['learnedSkills']
        skill_id = 1
        while learned_skills != 0:
            if learned_skills % 2 == 1:
                yield skill_id
            learned_skills //= 2
            skill_id += 1

    def _getCrewSkillsInfo(self):
        for e in self.entities.values():
            if e.get_name() == 'Vehicle':
                yield e.id, list(self._get_learned_skills(e))

    def onBattleEnd(self, avatar, teamId, state):
        self._battle_result = dict(
            winner_team_id=teamId,
            victory_type=state
        )

    def onNewPlayerSpawnedInBattle(self, avatar, pickle_data):
        self._players.create_or_update_players(
            pickle.loads(pickle_data))

    def onArenaStateReceived(self, avatar, arenaUniqueId, teamBuildTypeId, preBattlesInfo, playersStates,
                             observersState, buildingsInfo):
        self._arena_id = arenaUniqueId
        self._players.create_or_update_players(
            pickle.loads(playersStates))
        self.create_player_state_list()

    def onPlayerInfoUpdate(self, avatar, playersData, observersData):
        self._players.create_or_update_players(pickle.loads(playersData))
        self.update_player_state_list()

    def receiveDamageStat(self, avatar, blob):
        normalized = {}
        for (type_, bool_), value in pickle.loads(blob).items():
            # TODO: improve damage_map and list other damage types too
            if bool_ != DamageStatsType.DAMAGE_STATS_ENEMY:
                continue
            normalized.setdefault(type_, {}).setdefault(bool_, 0)
            normalized[type_][bool_] = value
        self._damage_map.update(normalized)

    def onRibbon(self, avatar, ribbon_id):
        self._ribbons.setdefault(avatar.id, {}).setdefault(ribbon_id, 0)
        self._ribbons[avatar.id][ribbon_id] += 1

    def onAchievementEarned(self, avatar, avatar_id, achievement_id):
        self._achievements.setdefault(avatar_id, {}).setdefault(achievement_id, 0)
        self._achievements[avatar_id][achievement_id] += 1

    def receiveVehicleDeath(self, avatar, killedVehicleId, fraggerVehicleId, typeDeath):
        self._death_map.append((killedVehicleId, fraggerVehicleId, typeDeath))

    def g_receiveDamagesOnShip(self, vehicle, damages):
        for damage_info in damages:
            self._shots_damage_map.setdefault(vehicle.id, {}).setdefault(damage_info['vehicleID'], 0)
            self._shots_damage_map[vehicle.id][damage_info['vehicleID']] += damage_info['damage']

    def receive_planeDeath(self, avatar, squadronID, planeIDs, reason, attackerId):
        self._dead_planes.setdefault(attackerId, 0)
        self._dead_planes[attackerId] += len(planeIDs)

    @property
    def map(self):
        raise NotImplemented()

    @map.setter
    def map(self, value):
        self._map = value.lstrip('spaces/')


def unpack_value(packed_value, value_min, value_max, bits):
    return packed_value / (2 ** bits - 1) * (abs(value_min) + abs(value_max)) - abs(value_min)


def unpack_values(packed_value, pack_pattern):
    values = []
    for i, pattern in enumerate(pack_pattern):
        min_value, max_value, bits = pattern
        value = packed_value & (2 ** bits - 1)

        values.append(unpack_value(value, min_value, max_value, bits))
        packed_value = packed_value >> bits
    try:
        assert packed_value == 0
    except AssertionError:
        pass
    return tuple(values)