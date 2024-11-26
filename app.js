document.addEventListener('DOMContentLoaded', () => {
    const seasonSelect = document.getElementById('season-select');
    const teamInput = document.getElementById('team-input');
    const fetchTeamBtn = document.getElementById('fetch-team-btn');
    const playersContainer = document.getElementById('players-container');
    const playerStatsContainer = document.getElementById('player-stats-container');

    const API_BASE_URL = 'http://localhost:5000';

    fetchTeamBtn.addEventListener('click', async () => {
        const team = teamInput.value.trim();
        const season = seasonSelect.value;

        if (!team) {
            alert('Please enter a team name');
            return;
        }

        try {
            // Fetch team players
            const response = await fetch(`${API_BASE_URL}/get_team_players?team=${team}&season=${season}`);
            const players = await response.json();

            // Clear previous results
            playersContainer.innerHTML = '<h2 class="font-bold mb-2">Team Players:</h2>';
            playerStatsContainer.innerHTML = '';

            if (players.error) {
                playersContainer.innerHTML += `<p class="text-red-500">${players.error}</p>`;
                return;
            }

            // Create player buttons
            players.forEach((player, index) => {
                const playerBtn = document.createElement('button');
                playerBtn.textContent = `${player.name} (${player.position}) #${player.jersey}`;
                playerBtn.classList.add('block', 'w-full', 'p-2', 'mb-2', 'bg-gray-200', 'rounded', 'hover:bg-gray-300');
                
                playerBtn.addEventListener('click', async () => {
                    try {
                        // Fetch regular season stats
                        const regularSeasonStatsResponse = await fetch(`${API_BASE_URL}/get_player_stats?player_id=${player.id}&season=${season}&is_playoffs=false`);
                        const regularSeasonStats = await regularSeasonStatsResponse.json();

                        // Fetch playoff stats
                        const playoffStatsResponse = await fetch(`${API_BASE_URL}/get_player_stats?player_id=${player.id}&season=${season}&is_playoffs=true`);
                        const playoffStats = await playoffStatsResponse.json();

                        if (regularSeasonStats.error && playoffStats.error) {
                            playerStatsContainer.innerHTML = `<p class="text-red-500">No stats found</p>`;
                            return;
                        }

                        // Generate stats display
                        let statsHTML = `<h2 class="font-bold mb-2">Stats for ${player.name}:</h2>`;

                        // Regular Season Stats
                        if (!regularSeasonStats.error) {
                            statsHTML += `
                            <div class="bg-blue-100 p-4 rounded mb-4">
                                <h3 class="font-semibold mb-2">Full Season Performance (Including Playoffs)</h3>
                                <p>Games Played: ${regularSeasonStats.games_played}</p>
                                <p>Points per Game: ${regularSeasonStats.ppg}</p>
                                <p>Rebounds per Game: ${regularSeasonStats.rpg}</p>
                                <p>Assists per Game: ${regularSeasonStats.apg}</p>
                                <p>Field Goal %: ${regularSeasonStats.fg_percentage}%</p>
                                <p>3-Point %: ${regularSeasonStats.three_point_percentage}%</p>
                            </div>
                            `;
                        }

                        playerStatsContainer.innerHTML = statsHTML;
                    } catch (error) {
                        playerStatsContainer.innerHTML = `<p class="text-red-500">Error fetching player stats</p>`;
                    }
                });

                playersContainer.appendChild(playerBtn);
            });
        } catch (error) {
            playersContainer.innerHTML = `<p class="text-red-500">Error fetching team players</p>`;
        }
    });
});