import json

from bs4 import BeautifulSoup
from bs4.element import NavigableString

from request import request
from Config.config import LOL_VERSION
from Bot.models import Champion, Result
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
        
        self.elo_list: list[str] = ['overall', 'challenger', 'master', 'grandmaster', 'diamond', 'platinum', 'emerald',  
                                    'gold', 'silver', 'bronze', 'iron', 'diamond_2_plus', 'master_plus', 
                                    'diamond_plus', 'platinum_plus', '']
        
        self.all_champions: list[str] = self._get_champion_list()
        
        self.role_list: list[str] = ['top', 'jungle', 'mid', 'adc', 'support']
        
        self.ugg_div_values: list[str] = ['shinggo', 'good', 'okay', 'volxd', 'meh', 'great'] # Don't ask
        self.ugg_div_values_reversed: list[str] = list(reversed(self.ugg_div_values))
        

    def _get_champion_list(self) -> list[str]:
        """Gets list of champions."""
        self.logger.debug("Fetching champion.json")
        url: str = f"https://ddragon.leagueoflegends.com/cdn/{LOL_VERSION}/data/en_US/champion.json"
        self.logger.debug("Finished fetching champion.json")
        
        champion_response = request(url)
        champion_json: dict[str, str] = json.loads(champion_response.text)
        return [i.lower() for i in champion_json['data']]
         
    
    def _alternative_elo_check(self, elo: str) -> str:
        """Checks if elo in alternative elos

        Args:
            elo (str): elo

        Returns:
            str: input elo if not found, else elo
        """
        for key, value in self.alternative_elos.items():
            if elo in value:
                return key
        
        return elo
        
    
    def _get_url(self, champ: Champion) -> str:
        """Returns the url to fetch
        Returns:
            str: url
        """
        elo_str = ""
        opponent_str = ""
        role_str = ""
        
        if champ.elo:
            elo_str = f"&rank={champ.elo}"
        
        if champ.opponent:
            opponent_str = f"&opp={champ.opponent}"
            
        if champ.role:
            role_str: str = f"{champ.role}"
        
        if role_str:
            self.logger.debug(f"Created url https://u.gg/lol/champions/{champ.name}/build/{role_str}?{elo_str}{opponent_str}")
            return f"https://u.gg/lol/champions/{champ.name}/build/{role_str}?{elo_str}{opponent_str}"
        
        self.logger.debug(f"Created url https://u.gg/lol/champions/{champ.name}/build?{elo_str}{opponent_str}")
        return f"https://u.gg/lol/champions/{champ.name}/build?{elo_str}{opponent_str}"
    
    
    def _get_winrate(self, soup: BeautifulSoup) -> str | None:
        for value in self.ugg_div_values:
            elements = soup.find_all(
                'div',
                {'class': f'text-[20px] max-sm:text-[16px] max-xs:text-[14px] font-extrabold {value}-tier'}
            )
            for el in elements:
                text = el.get_text(strip=True)
                if '%' in text and any(ch.isdigit() for ch in text):
                    return text
        return None
    
    
    #def _get_winrate(self, soup: BeautifulSoup) -> str | None:
    #    """Fetches the winrate of a champ
    #    Returns:
    #        float | None: Winrate if found else None
    #    """
    #    win_rate: None | NavigableString = None
    #    
    #    for value in self.ugg_div_values:
    #        win_rate = soup.find('div', {'class':f'text-[20px] max-sm:text-[16px] max-xs:text-[14px] font-extrabold {value}-tier'}) # type: ignore
    #        if win_rate is not None:
    #            win_rate = win_rate.text # type: ignore
    #            break        
    #    
    #    
    #    try:
    #        int(win_rate[0]) # type: ignore
    #    except (ValueError, TypeError, AttributeError):
    #        win_rate = None
    #        for value in self.ugg_div_values_reversed:
    #            win_rate = soup.find('div', {'class':f'text-[20px] max-sm:text-[16px] max-xs:text-[14px] font-extrabold {value}-tier'}) # type: ignore
    #            if win_rate is not None:
    #                win_rate = win_rate.text # type: ignore
    #                break
    #            
    #    
    #    # For finding the value when tier and winrate have the same div value
    #    # One of the ugliest functions ever written
    #    try:
    #        int(win_rate[0]) # type: ignore
    #    except (ValueError, TypeError, AttributeError):
    #        win_rate = None
    #        for value in self.ugg_div_values:
    #            win_rate = soup.find('div', {'class':f'text-[20px] max-sm:text-[16px] max-xs:text-[14px] font-extrabold {value}-tier'}) # type: ignore
    #            try:
    #                int(win_rate[0].text[0]) #type: ignore
    #                win_rate = win_rate[0] # type: ignore
    #            except (ValueError, KeyError):
    #                try:
    #                    int(win_rate[1].text[0]) #type: ignore
    #                    win_rate = win_rate[1] # type: ignore
    #                except (ValueError, KeyError, TypeError, IndexError):
    #                    continue
    #            except (TypeError, IndexError):
    #                continue
    #        
    #        win_rate = win_rate.text # type: ignore
    #    
    #    return win_rate if win_rate is not None else None
    
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
        
        soup = BeautifulSoup(web, "html.parser") # type: ignore
        
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
        
        final_string = f" with {match_count} matches played, a {pick_rate} pick rate and a {ban_rate} ban rate" # type: ignore
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
        
        soup = BeautifulSoup(web, "html.parser") # type: ignore
        
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
            if arg in self.all_champions:
                champ.opponent = arg
                continue
            
            if arg in self.role_list:
                champ.role = arg
                continue
                
            arg = self._alternative_elo_check(arg)
            if arg in self.elo_list:
                champ.elo = arg
            
            
        if not champ.opponent:
            return self._get_all_no_opponent(champ)
            
        return self._get_all_with_opponent(champ)