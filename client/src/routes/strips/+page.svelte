<script lang="ts">
	import { onMount } from 'svelte';
	import Strip from '@definitions/strip';
	import Segment from '@definitions/segment';
	import Vec2 from '@definitions/vec2';

	let selectedStrip: Strip | null = null;
	let selectedSegment: Segment | null = null;
	let strips: Strip[] = [];
	let canvas: HTMLCanvasElement;
	let context: CanvasRenderingContext2D;
	let templateInput: HTMLInputElement;
	let template: HTMLImageElement;

	function createSegment() {
		if (!selectedStrip) {
			return;
		}
		const newSegment = new Segment();
		selectedStrip.addSegment(newSegment);
		strips = strips;
		selectedSegment = newSegment;
	}

	function selectSegment(segment: Segment) {
		selectedSegment = segment;
		redraw();
	}

	function deleteSegment(segment: Segment) {
		if (selectedStrip == null) {
			return;
		}
		const index = selectedStrip.segments.indexOf(segment);
		selectedStrip.segments.splice(index, 1);
		strips = strips;
		redraw();
	}

	function createStrip() {
		let newStrip = new Strip();
		strips = [...strips, newStrip];
		selectStrip(newStrip);
	}

	function selectStrip(strip: Strip) {
		selectedStrip = strip;
		selectedSegment = null;

		if (strip) {
			template.src = strip.template;
		}
	}

	function deleteStrip(strip: Strip) {
		const index = strips.indexOf(strip);
		strips.splice(index, 1);
		strips = strips;
	}

	function exportStrip(strip: Strip) {
		console.log(JSON.stringify(strip.layout));
	}

	onMount(() => {
		canvas.width = canvas.offsetWidth;
		canvas.height = canvas.offsetHeight;

		context = canvas.getContext('2d');

		if (!context) {
			return;
		}

		strips = JSON.parse(localStorage.getItem('strips')) || [];
		strips = strips.map((strip) => {
			strip.segments = strip.segments.map((segment) => {
				return Object.assign(new Segment(), segment);
			});

			return Object.assign(new Strip(), strip);
		});

		if (strips.length > 0) {
			selectStrip(strips[0]);

			template.setAttribute('src', selectedStrip.template);

			if (selectedStrip.segments.length > 0) {
				selectSegment(selectedStrip.segments[0]);
			}
		}

		redraw();

		setInterval(() => {
			console.log('saving strips', strips);
			localStorage.setItem('strips', JSON.stringify(strips));
		}, 30000);

		console.log('selectedStrip', selectedStrip);
		console.log('selectedSegment', selectedSegment);
	});

	function canvasClicked(ev: MouseEvent) {
		if (selectedStrip == null) {
			return;
		}

		if (!selectedSegment) {
			selectedSegment = new Segment();
			selectedStrip.addSegment(selectedSegment);
		}

		selectedSegment.addPoint(
			new Vec2(ev.clientX - canvas.offsetLeft, ev.clientY - canvas.offsetTop)
		);

		selectedStrip.createLayout();
	}

	function redraw() {
		if (context == null) {
			return;
		}

		context.clearRect(0, 0, canvas.width, canvas.height);

		if (selectedStrip == null) {
			return;
		}

		let previousSegmentPoint = null;
		for (var segment of selectedStrip.segments) {
			if (segment.points.length == 0) {
				continue;
			}

			const firstPoint = segment.points[0];

			context.beginPath();

			// If first segment just move to start
			if (!previousSegmentPoint) {
				context.moveTo(firstPoint.x, firstPoint.y);
			}
			// If 2nd+ segment draw dotted lines to end of previous segment
			else {
				context.moveTo(previousSegmentPoint.x, previousSegmentPoint.y);
				context.lineTo(firstPoint.x, firstPoint.y);
				context.setLineDash([5, 5]);
				context.strokeStyle = '#0000ff';
				context.stroke();

				context.beginPath();
				context.setLineDash([]);
			}

			// Draw lines
			for (let point of segment.points) {
				context.lineTo(point.x, point.y);
			}
			context.strokeStyle = '#ff0000';
			context.stroke();

			// Draw control points
			for (let point of segment.points) {
				context.beginPath();
				context.arc(point.x, point.y, 8, 0, 2 * Math.PI);
				context.strokeStyle = '#00ff00';
				context.stroke();
				previousSegmentPoint = point;
			}
		}

		if (selectedStrip.layout) {
			for (let led of selectedStrip.layout.leds) {
				context.beginPath();
				context.arc(led.x, led.y, 4, 0, 2 * Math.PI);
				context.strokeStyle = '#ff00ff';
				context.stroke();
			}
		}
	}

	function templateChanged(ev: Event) {
		if (
			context == null ||
			selectedStrip == null ||
			templateInput == null ||
			templateInput.files == null ||
			selectedStrip == null
		) {
			return;
		}

		const file = templateInput.files[0];

		if (file) {
			const reader = new FileReader();
			reader.addEventListener('load', function () {
				selectedStrip.template = reader.result;
				template.setAttribute('src', reader.result);
			});
			reader.readAsDataURL(file);
		}
	}

	function layoutChanged() {
		if (!selectedStrip) {
			return;
		}

		selectedStrip.createLayout();
		redraw();
	}
</script>

<aside id="aside">
	<button on:click={createStrip}>Create new strip</button>
	{#each strips as strip}
		<div class={selectedStrip == strip ? 'active' : ''}>
			<button on:click={(_) => selectStrip(strip)}>select</button>
			<button on:click={(_) => deleteStrip(strip)}>delete</button>
			<p>name:</p>
			<input bind:value={strip.name} />
			<p>length (m):</p>
			<input type="number" bind:value={strip.lengthMeters} on:change={layoutChanged} />
			<p>total leds:</p>
			<input type="number" bind:value={strip.totalLeds} on:change={layoutChanged} />

			<p>template:</p>
			<input
				bind:this={templateInput}
				bind:value={strip.template}
				type="file"
				on:change={templateChanged}
			/>
			<p>template scale:</p>
			<input type="number" bind:value={strip.templateScale} on:change={layoutChanged} />

			<p>segments:</p>
			<button on:click={createSegment}>Create new segment</button>
			{#each strip.segments as segment, i}
				<div class={selectedSegment == segment ? 'active' : ''}>
					<button on:click={(_) => selectSegment(segment)}>select</button>
					<input bind:value={segment.name} />
					<button on:click={(_) => deleteSegment(segment)}>x</button>
				</div>
			{/each}

			<button on:click={(_) => exportStrip(strip)}>Export</button>
		</div>
	{/each}


</aside>
<canvas id="canvas" bind:this={canvas} on:click={canvasClicked} />
<img id="template" bind:this={template} alt="no template" />

<style>
	.active {
		border: 1px solid orangered;
	}

	#aside {
		display: grid;
		grid-auto-flow: row;
		grid-area: nav;
	}

	#canvas {
		grid-area: main;
		height: 100%;
		width: 100%;
		z-index: 2;
	}

	#template {
		grid-area: main;
		align-self: center;
		justify-self: center;
		width: 50%;
		object-fit: cover;
		overflow: hidden;
		text-align: center;
		z-index: 1;
	}
</style>
