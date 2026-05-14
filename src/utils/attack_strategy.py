from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class DeploySpeedSettings:
    wave_deployment_speed: int = 8
    troop_deployment_speed: int = 7
    description: str = "Controls army deployment timing"
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**{k: v for k, v in data.items() if k in ('wave_deployment_speed', 'troop_deployment_speed')})


@dataclass
class StrategySettings:
    attack_sides: Dict[str, bool] = None
    split_waves: int = 1
    deploy_near_red_lines: bool = True
    deploy_near_collectors: bool = True
    
    def __post_init__(self):
        if self.attack_sides is None:
            self.attack_sides = {"NW": True, "NE": True, "SW": True, "SE": True}
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            attack_sides=data.get('attack_sides', {"NW": True, "NE": True, "SW": True, "SE": True}),
            split_waves=data.get('split_waves', 1),
            deploy_near_red_lines=data.get('deploy_near_red_lines', True),
            deploy_near_collectors=data.get('deploy_near_collectors', True)
        )


@dataclass
class HeroAbilitySettings:
    activate_after_seconds: int = 10
    enabled: bool = True
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            activate_after_seconds=data.get('activate_after_seconds', 10),
            enabled=data.get('enabled', True)
        )


@dataclass
class HumanLikeVariations:
    enable_mouse_parking: bool = True
    enable_hesitation: bool = True
    min_hesitation_ms: int = 200
    max_hesitation_ms: int = 800
    coordinate_variance_pixels: int = 5
    click_jitter_pixels: int = 3
    description: str = "Maintains human-like behavior to avoid detection"
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            enable_mouse_parking=data.get('enable_mouse_parking', True),
            enable_hesitation=data.get('enable_hesitation', True),
            min_hesitation_ms=data.get('min_hesitation_ms', 200),
            max_hesitation_ms=data.get('max_hesitation_ms', 800),
            coordinate_variance_pixels=data.get('coordinate_variance_pixels', 5),
            click_jitter_pixels=data.get('click_jitter_pixels', 3)
        )


@dataclass
class EndBattleSettings:
    end_if_no_resources_for_seconds: int = 10
    enabled: bool = True
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            end_if_no_resources_for_seconds=data.get('end_if_no_resources_for_seconds', 10),
            enabled=data.get('enabled', True)
        )


@dataclass
class AttackStrategyConfig:
    deploy_speed: DeploySpeedSettings = None
    strategy: StrategySettings = None
    hero_ability: HeroAbilitySettings = None
    end_battle: EndBattleSettings = None
    human_like_variations: HumanLikeVariations = None
    
    def __post_init__(self):
        if self.deploy_speed is None:
            self.deploy_speed = DeploySpeedSettings()
        if self.strategy is None:
            self.strategy = StrategySettings()
        if self.hero_ability is None:
            self.hero_ability = HeroAbilitySettings()
        if self.end_battle is None:
            self.end_battle = EndBattleSettings()
        if self.human_like_variations is None:
            self.human_like_variations = HumanLikeVariations()
    
    def to_dict(self) -> Dict:
        return {
            'deploy_speed': self.deploy_speed.to_dict(),
            'strategy': self.strategy.to_dict(),
            'hero_ability': self.hero_ability.to_dict(),
            'end_battle': self.end_battle.to_dict(),
            'human_like_variations': self.human_like_variations.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            deploy_speed=DeploySpeedSettings.from_dict(data.get('deploy_speed', {})),
            strategy=StrategySettings.from_dict(data.get('strategy', {})),
            hero_ability=HeroAbilitySettings.from_dict(data.get('hero_ability', {})),
            end_battle=EndBattleSettings.from_dict(data.get('end_battle', {})),
            human_like_variations=HumanLikeVariations.from_dict(data.get('human_like_variations', {}))
        )
    
    @classmethod
    def default(cls):
        return cls()
