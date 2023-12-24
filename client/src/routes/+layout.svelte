<nav class="nav">
	<a href="/">effects</a>
	<a href="/strips">strips</a>
</nav>

<main class="main">
	<slot />
</main>

<style>
	:global(.root) {
		display: grid;
		grid-auto-flow: row;
		grid-template-areas: 'nav' 'main';
        grid-template-rows: 64px auto;
	}

	.nav {
		grid-area: nav;
        display: grid;
        grid-auto-flow: column;
        gap: 2rem;
        justify-content: start;
        align-items: center;
        padding: 0 2rem;
	}

	.main {
		grid-area: main;
	}
</style>
