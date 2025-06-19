<script lang="ts">
	import { onMount, getContext, createEventDispatcher } from 'svelte';
	import { settings } from '$lib/stores';
	import Modal from './common/Modal.svelte';
	import { getWarningContent } from '$lib/utils/warning';

	interface WarningItem {
		title: string;
		content: string;
	}

	interface WarningSection {
		date?: string;
		items: WarningItem[];
	}

	interface Warning {
		important: WarningSection;
		note: WarningSection;
		tips: WarningSection;
	}

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let show = false;

	let warning: Warning | null = null;

	onMount(async () => {
		warning = await getWarningContent();
	});

	function handleConfirm() {
		show = false;
		dispatch('confirm');
	}
</script>

<Modal bind:show size="lg">
	<div class="px-5 pt-4 dark:text-gray-300 text-gray-700">
		<div class="flex justify-between items-start">
			<div class="text-xl font-semibold">
				{$i18n.t('File Upload Warning')}
			</div>
			<button
				class="self-center"
				on:click={() => {
					show = false;
				}}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 20 20"
					fill="currentColor"
					class="w-5 h-5"
				>
					<p class="sr-only" dir={$settings?.chatDirection ?? 'ltr'}>{$i18n.t('Close')}</p>
					<path
						d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"
					/>
				</svg>
			</button>
		</div>

		<div class="w-full p-4 text-gray-700 dark:text-gray-100">
			<div class="overflow-y-scroll max-h-96 scrollbar-hidden">
				<div class="mb-3">
					{#if warning}
						{#each Object.keys(warning) as section}
							<div class="mb-3 pr-2">
								<div
									class="font-semibold uppercase text-xs
                                    {section === 'important'
										? 'text-white bg-red-600'
										: section === 'note'
											? 'text-white bg-blue-600'
											: section === 'tips'
												? 'text-white bg-green-600'
												: 'text-white bg-gray-600'}  
                                    w-fit px-3 rounded-full my-2.5"
								>
									{section}
								</div>

								<div class="my-2.5 px-1.5">
									{#each warning[section].items as item}
										<div class="text-sm mb-2">
											<div class="font-semibold">
												{item.title}
											</div>
											<div class="mb-2 mt-1">{item.content}</div>
										</div>
									{/each}
								</div>
							</div>
						{/each}
					{/if}
				</div>
			</div>
			<div class="flex justify-end pt-3">
				<button
					on:click={handleConfirm}
					class="px-3.5 py-1.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full"
				>
					<span class="relative">{$i18n.t('I Understand')} 👍</span>
				</button>
			</div>
		</div>
	</div>
</Modal>
