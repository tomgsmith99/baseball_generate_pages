
			<div class="row">

				<div class="col-8">

					<h3 style="margin-top:10px">{{season}} Standings</h3>

					<table class="table table-striped">
					{{#owner_rows}}

						<tr>
							<td class="owner_row_cell_rt">{{place}}</td>
							<td class="owner_row_cell"><a href="#{{season}}_{{owner_id}}">{{nickname}}</a></td>
							<td class="owner_row_cell"><a href="#{{season}}_{{owner_id}}">{{team_name}}</a></td>
							<td class="owner_row_cell_rt">{{points}}</td>
							<td class="owner_row_cell_img"><img src='{{head_shot}}'/></td>
						</tr>

					{{/owner_rows}}
					</table>
				</div>

				<div class="col-4">

					<div id = "last_updated" style="margin-top:10px">
						<p>last updated: {{last_updated}}</p>
					</div>

					<div class="dropdown" style="margin-bottom: 10px">
						<button class="btn btn-info dropdown-toggle" type="button" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
							Owners {{season}}
						</button>

						<div class="dropdown-menu scrollable-menu" aria-labelledby="dropdownMenuButton">
						{{#owners}}
							<a class='dropdown-item' href='#{{season}}_{{owner_id}}'>{{nickname}}</a>
						{{/owners}}
						</div>
					</div>

					<div id="players_link" style="margin-bottom: 10px">
						<a target = "_blank" href = "/seasons/{{season}}/players">
							<button class="btn btn-info" type="button">
							Players {{season}}
						</button>
						</a>
					</div>

					<div id="trades_link" style="margin-bottom: 10px">
						<a target = "_blank" href = "/seasons/{{season}}/trades">
							<button class="btn btn-info" type="button">
							Trades {{season}}
						</button>
						</a>
					</div>

					<!-- leaderboard -->

					<div id="yesterday_owners">
						<table class="table table-sm table-striped">
							<thead>
								<tr>
									<th colspan="6">
										<a target = "_blank" href = "">Yesterday's top owners</a>
									</th>
								</tr>
							</thead>

							<tbody>
								{{yesterday_top_owners}}
							</tbody>
						</table>
					</div>

					<div id="hot_owners">
						<table class="table table-sm table-striped">
							<thead>
								<tr>
									<th colspan="6">
										<a target = "_blank" href = "">Hot owners</a>
									</th>
								</tr>
							</thead>

							<tbody>
								{{hot_owners}}
							</tbody>
						</table>
					</div>

					<div id="yesterday_players">
						<table class="table table-sm table-striped">
							<thead>
								<tr>
									<th colspan="6">
										<a target = "_blank" href = "">Yesterday's top players (picked)</a>
									</th>
								</tr>
							</thead>

							<tbody>
								{{yesterday_top_players-picked}}
							</tbody>
						</table>
					</div>

					<div id="hot_players">
						<table class="table table-sm table-striped">
							<thead>
								<tr>
									<th colspan="6">
										<a target = "_blank" href = "">Hot players (picked)</a>
									</th>
								</tr>
							</thead>

							<tbody>
								{{hot_players-picked}}
							</tbody>
						</table>
					</div>

					<div id="players_prod_picked">
						<table class="table table-sm table-striped">
							<thead>
								<tr>
									<th colspan="6">
										<a target = "_blank" href = "/players/{{season}}">Most Productive Players (picked)</a>
									</th>
								</tr>
							</thead>

							<tbody>
								{{most_productive_players-picked}}
							</tbody>
						</table>
					</div>

					<div id="players_val">
						<table class="table table-sm table-striped">
							<thead>
								<tr>
									<th colspan="6">
										<a target = "_blank" href = "/players/{{season}}">Most Valuable Players (picked)</a>
									</th>
								</tr>
							</thead>

							<tbody>
								{{most_valuable_players-picked}}
							</tbody>
						</table>
					</div>

					<div id="players_picked">
						<table class="table table-sm table-striped">
							<thead>
								<tr>
									<th colspan="6">
										<a target = '_blank' href = "/players/{{season}}">Most Popular Players</a>
									</th>
								</tr>
							</thead>

							<tbody>
								{{most_popular_players}}
							</tbody>
						</table>
					</div>

					<div id="players_prod_all">
						<table class="table table-sm table-striped">
							<thead>
								<tr>
									<th colspan="6">
										<a target = "_blank" href = "/players/{{season}}">Most Productive Players (all)</a>
									</th>
								</tr>
							</thead>

							<tbody>
								{{most_productive_players-all}}
							</tbody>
						</table>
					</div>

					<div id="players_val_all">

						<table class="table table-sm table-striped">
							<thead>
								<tr>
									<th colspan="6">
										<a target = "_blank" href = "/players/{{season}}">Most Valuable Players (all)</a>
									</th>
								</tr>
							</thead>

							<tbody>
								{{most_valuable_players-all}}
							</tbody>
						</table>
					</div>
				</div>
			</div>

			<div class="row">

				<div class="col-8">

					{{#teams}}

<a id="{{season}}_{{owner_id}}"></a>

<table class="table table-striped table-bordered table-sm">
	<thead>
		<tr>
			<th colspan="10">{{nickname}} - {{team_name}}</th>
		</tr>

		<tr><th colspan="10">{{season}}: {{place}} place</th></tr>

		<tr>
			<th>POS</th>
			<th>Name</th>
			<th class="text-center">Team</th>
			<th class="text-center">Salary</th>
			<th class="text-center">Pts</th>
			<th class="text-center">Yday</th>
			<th class="text-center">Rec</th>
			<th class="text-center">Val</th>
		</tr>
	</thead>

	<tbody>

		{{#active_players}}

		{{^acquired}}<tr>{{/acquired}}

		{{#acquired}}<tr style="font-style: italic">{{/acquired}}

			<td>{{pos}}</td>
			<td><a href='/players/{{player_id}}'>{{fnf}}</a></td>
			<td>{{team}}</td>
			<td class="player_row_cell_rt">${{salary}}</td>
			<td class="player_row_cell_rt">{{points}}</td>
			<td class="player_row_cell_rt">{{yesterday}}</td>
			<td class="player_row_cell_rt">{{recent}}</td>
			<td class="player_row_cell_rt">{{value}}</td>
		</tr>
		{{/active_players}}

		{{#has_benched_players}}
		<tr><td colspan="10" style="text-align: center;">Benched players</td></tr>
		{{/has_benched_players}}

		{{#benched_players}}
		<tr>
			<td>{{pos}}</td>
			<td><a href='/players/{{player_id}}'>{{fnf}}</a></td>
			<td>{{team}}</td>
			<td class="player_row_cell_rt">${{salary}}</td>
			<td class="player_row_cell_rt">{{points}}</td>
			<td class="player_row_cell_rt">{{yesterday}}</td>
			<td class="player_row_cell_rt">{{recent}}</td>
			<td class="player_row_cell_rt">{{value}}</td>
		</tr>

		{{/benched_players}}

		<tr>
			<td colspan="3" align="right">bank: ${{bank}}</td>
			<td align="right"><b>${{salary}}</b></td>
			<td align="right"><b>{{points}}</b></td>
			<td align="right"><b>{{yesterday}}</b></td>
			<td align="right"><b>{{recent}}</b></td>
			<td align="right"><a href = "#top">top</a></td>
		</tr>
	</tbody>
</table>

					{{/teams}}

				</div>

			</div>
