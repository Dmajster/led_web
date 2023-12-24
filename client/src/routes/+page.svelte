<script lang="ts">
	let colors: string[] = [];

	function update() {
		console.log('updating', colors);
		fetch('http://lisica.lan/update', {
			method: 'POST',
			body: JSON.stringify({
				colors: colors.map((ledColor) => hexToRgb(ledColor))
			}),
			headers: {
				'Content-type': 'application/json; charset=UTF-8'
			}
		});
	}

	function hexToRgb(hex: string) {
		return hex
			.replace(/^#?([a-f\d])([a-f\d])([a-f\d])$/i, (m, r, g, b) => '#' + r + r + g + g + b + b)
			.substring(1)
			.match(/.{2}/g)
			.map((x) => parseInt(x, 16));
	}

	function addColor() {
		colors = [...colors, '#ffffff'];
	}
</script>

<button on:click={addColor}>Add color</button>
{#each colors as color}
	<input type="color" bind:value="{color}" on:change={update} />
{/each}
