
{{#sections}}

<h3 style = "margin-top: 10px">{{section_title}}</h3>

<h4>{{range}}</h3>

<div class="row">

	<div class="col-6">

		{{{html}}}

	</div>

	<div class="col-6">

		{{#img}}
		<span class="align-middle">

		<figure class="figure">

			<img class="figure-img img-fluid rounded" src="{{img}}">

			<figcaption class="figure-caption">{{caption}}</figcaption>

		</figure>

		</span>
		{{/img}}

	</div>
</div>

{{/sections}}
