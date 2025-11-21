import json

from bs4 import BeautifulSoup

from request import request
from Bot.models import Champion, Result, WinrateNotFoundException
from logger import SingletonLogger


class WinrateFetcher:
    """Used to get winrates
    """
    def __init__(self) -> None:
        
        self.logger = SingletonLogger().get_logger()
        
        self.alternative_elos: dict[str, list[str]] = {
            'platinum_plus': ['platplus', 'plat+', 'platinumplus'],
            'diamond_2_plus': ['d2+', 'd2', 'd2plus', 'diamond2', 'diamond2plus', 'diamond2+', 'diamond_2plus', 'diamond_2+'],
            'diamond_plus': ['d+', 'dplus', 'diamondplus'],
            'master_plus': ['m+', 'master+', 'masterplus', 'masters', 'masters+', 'mastersplus'],
            'emerald_plus' : ['eme+', 'emerald+', 'emeplus', 'emeraldplus']
        }
        
        self.alternative_champions: dict[str, list[str]] = {
            'monkeyking': ['wukong'],
            'drmundo': ['mundo'],
            'kogmaw': ["kog'maw"],
            'jarvaniv': ['jarvan'],
            'khazix': ["kha'zix"],
            'ksante': ["k'sante"],
            'masteryi': ['yi'],
            'aatrox': ['emo'],
            'tahmkench': ['tahm'],
            'twistedfate': ['tf'],
            'xinzhao': ['xin'],
            'aurelionsol': ['asol'],
            'leesin': ['lee']
        }
        
        self.elo_list: list[str] = ['overall', 'challenger', 'master', 'grandmaster', 'diamond', 'platinum', 'emerald',  
                                    'gold', 'silver', 'bronze', 'iron', 'diamond_2_plus', 'master_plus', 
                                    'diamond_plus', 'platinum_plus', '']
        
        self._elo_lookup: dict[str, str] = {
            alt: key for key, values in self.alternative_elos.items() for alt in values
        }
        
        self._champion_lookup: dict[str, str] = {
            alt: key for key, values in self.alternative_champions.items() for alt in values
        }
        
        
        self.patch_version: str = self._get_current_patch()
        self.patch_minor_version: str = self.patch_version.split('.')[1]
        
        self.all_champions: list[str] = self._get_champion_list()
        
        self.role_list: list[str] = ['top', 'jungle', 'mid', 'adc', 'support']
        
        self.ugg_div_values: list[str] = ['shinggo', 'good', 'okay', 'volxd', 'meh', 'great'] # Don't ask
        self.ugg_div_values_reversed: list[str] = list(reversed(self.ugg_div_values))
        

    def _get_champion_list(self) -> list[str]:
        """Gets list of champions."""
        self.logger.debug("Fetching champion.json")
        url: str = f"https://ddragon.leagueoflegends.com/cdn/{self.patch_version}/data/en_US/champion.json"
        self.logger.debug("Finished fetching champion.json")
        
        champion_response = request(url)
        champion_json: dict[str, str] = json.loads(champion_response.text)
        return [i.lower() for i in champion_json['data']]
    
    
    def _get_current_patch(self) -> str:
        self.logger.debug("Fetching current patch.")
        url = 'https://ddragon.leagueoflegends.com/realms/na.json'
        patch_response = request(url)
        
        patch: str = json.loads(patch_response.content)['v']
        return patch
        
    
    def _alternative_elo_check(self, elo: str) -> str:
        return self._elo_lookup.get(elo, elo)
    
    def _alternate_champion_check(self, name: str) -> str:
        return self._champion_lookup.get(name, name)
    
    def _check_patch(self, patch: str) -> str:
        # Standard patch format: ab.cd, example 15.21
        if ((len(patch) == 5 or len(patch) == 4) 
            and patch[2] == '.'
            and patch[:2].isdigit()
            and patch[3:].isdigit()):
            return patch
        
        return "" 
        
    
    def _get_url(self, champ: Champion) -> str:
        """Returns the url to fetch
        Returns:
            str: url
        """
        elo_str = ""
        opponent_str = ""
        role_str = ""
        patch_str = ""
        
        if champ.elo:
            elo_str = f"&rank={champ.elo}"
        
        if champ.opponent:
            opponent_str = f"&opp={champ.opponent}"
            
        if champ.role:
            role_str = f"{champ.role}"
        
        if champ.patch:
            patch_str = f"&patch={champ.patch.replace('.', '_')}"
        
        if role_str:
            self.logger.debug(f"Created url https://u.gg/lol/champions/{champ.name}/build/{role_str}?{elo_str}{opponent_str}{patch_str}")
            return f"https://u.gg/lol/champions/{champ.name}/build/{role_str}?{elo_str}{opponent_str}{patch_str}"
        
        self.logger.debug(f"Created url https://u.gg/lol/champions/{champ.name}/build?{elo_str}{opponent_str}{patch_str}")
        return f"https://u.gg/lol/champions/{champ.name}/build?{elo_str}{opponent_str}{patch_str}"
    
    
    def _get_winrate(self, soup: BeautifulSoup) -> str:
        for value in self.ugg_div_values:
            elements = soup.find_all('div', {'class': f'text-[20px] max-sm:text-[16px] max-xs:text-[14px] font-extrabold {value}-tier'})
            for element in elements:
                text = element.get_text(strip=True)
                if '%' in text and any(char.isdigit() for char in text):
                    return text
        raise WinrateNotFoundException()
    
    
    def _get_match_count(self, soup: BeautifulSoup, with_opponent: bool) -> str | None:
        """Returns match count of a champ

        Args:
            soup (BeautifulSoup): BeautifulSoup instance
            with_opponent (bool): If opponent is given

        Returns:
            int | None: Match count if found else None
        """
        if not with_opponent:
            try:
                match_count: str = soup.find_all('div', {'class':'text-[20px] max-sm:text-[16px] max-xs:text-[14px] font-extrabold'})[3].text
            except IndexError:
                return None
        else:
            match_count: str = soup.find('div', {'class':'text-[20px] max-sm:text-[16px] max-xs:text-[14px] font-extrabold'}).text # type: ignore
             
        return match_count if match_count is not None else None
    
    def _get_pick_rate(self, soup: BeautifulSoup) -> str | None:
        """Returns pick rate of a champ

        Args:
            soup (BeautifulSoup): BeautifulSoup instance

        Returns:
            float | None: Pick rate if found else None
        """
        try:
            pick_rate: str = soup.find_all('div', {'class':'text-[20px] max-sm:text-[16px] max-xs:text-[14px] font-extrabold'})[1].text
        except IndexError:
            return None
        
        return pick_rate
    
    def _get_ban_rate(self, soup: BeautifulSoup) -> str | None:
        """Returns ban rate of a champ

        Args:
            soup (BeautifulSoup): BeautifulSoup instance

        Returns:
            float | None: Ban rate if found else None
        """
        try:
            ban_rate: str = soup.find_all('div', {'class':'text-[20px] max-sm:text-[16px] max-xs:text-[14px] font-extrabold'})[2].text
        except IndexError:
            return None
        
        return ban_rate

    def _get_all_no_opponent(self, champ: Champion) -> Result:
        url = self._get_url(champ)
        web = request(url).content
        
        soup = BeautifulSoup(web, "html.parser") 
        
        win_rate = self._get_winrate(soup)
        match_count = self._get_match_count(soup, with_opponent=False)
        pick_rate = self._get_pick_rate(soup)
        ban_rate = self._get_ban_rate(soup)
        
        if not match_count:
            self.logger.error(f"Unable to fetch match count for {champ=} with {url=}")
            
        if not pick_rate:
            self.logger.error(f"Unable to fetch pick rate for {champ=} with {url=}")
            
        if not ban_rate:
            self.logger.error(f"Unable to fetch ban_rate for {champ=} with {url=}")
        
        final_string = f" with {match_count} matches played, a {pick_rate} pick rate and a {ban_rate} ban rate"
        self.logger.debug(f"Final string for {champ=} : {final_string}")
        
        
        
        result = Result(champ=champ, 
                        win_rate=win_rate, 
                        with_opponent=True, 
                        match_count=match_count,
                        final_string=final_string
                        )
        
        return result
        
    def _get_all_with_opponent(self, champ: Champion) -> Result:
        url = self._get_url(champ)
        web = request(url).content
        
        soup = BeautifulSoup(web, "html.parser") 
        
        win_rate = self._get_winrate(soup)
        match_count = self._get_match_count(soup, with_opponent=True)
        
        if not match_count:
            self.logger.error(f"Unable to fetch match count for {champ=} with {url=}")
        
        result = Result(champ=champ,
                        with_opponent=False,
                        win_rate=win_rate,
                        match_count=match_count,
                        final_string=f" against {champ.opponent.capitalize()} with {match_count} matches played" # type: ignore
                        )
        
        return result
        
    
    def get_stats(self, champ: Champion, args: tuple[str, ...]) -> Result:
        for arg in args:
            arg = arg.lower()
            
            arg = self._alternate_champion_check(arg)
            if arg in self.all_champions:
                champ.opponent = arg
                continue
            
            if arg in self.role_list:
                champ.role = arg
                continue
            
            if self._check_patch(arg):
                champ.patch = arg
                continue
                
            arg = self._alternative_elo_check(arg)
            if arg in self.elo_list:
                champ.elo = arg
            
            
        if not champ.opponent:
            return self._get_all_no_opponent(champ)
            
        return self._get_all_with_opponent(champ)