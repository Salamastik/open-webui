<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { Confetti } from 'svelte-confetti';
	import { createEventDispatcher } from 'svelte';

	import { WEBUI_NAME, config, settings } from '$lib/stores';

	import { WEBUI_VERSION } from '$lib/constants';
	import { getWarning } from '$lib/apis';

	import Modal from './common/Modal.svelte';
	import { updateUserSettings } from '$lib/apis/users';

	const i18n = getContext('i18n');

	export let show = false;

	let warning = null;

	const dispatch = createEventDispatcher();

	onMount(async () => {
		const res = await getWarning();
		warning = res;
	});
</script>

<Modal bind:show size="sm" style="max-width: 420px;">
	<div class="px-5 pt-4 dark:text-gray-300 text-gray-700" style="direction: rtl;">
		<div class="flex justify-between items-start">
			<div class="text-xl font-semibold flex items-center gap-2 relative z-20">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-7 h-7 text-yellow-500"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="#FEF3C7" />
					<path
						stroke="#F59E42"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M12 8v4m0 4h.01"
					/>
				</svg>
				{$i18n.t('לפני העלאת מסמך - שימו ❤')}
			</div>
			<button
				class="self-center"
				on:click={() => {
					localStorage.version = $config.version;
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
		<!-- <div class="flex items-center mt-1">
			<div class="text-sm dark:text-gray-200">{$i18n.t('Release Notes')}</div>
			<div class="flex self-center w-[1px] h-6 mx-2.5 bg-gray-200 dark:bg-gray-700" />
			<div class="text-sm dark:text-gray-200">
				v{WEBUI_VERSION}
			</div>
		</div> -->
	</div>

	<div class=" w-full p-4 px-5 text-gray-700 dark:text-gray-100" dir="rtl">
		<div class=" overflow-y-scroll max-h-96 scrollbar-hidden">
			<div class="mb-3">
				{#if warning}
					{#each Object.keys(warning) as version}
						<div class=" mb-3 pr-2">
							<!-- <div class="font-semibold text-xl mb-1 dark:text-white">
								{warning[version].date}
							</div> -->

							<!-- <hr class="border-gray-100 dark:border-gray-850 my-2" /> -->

							{#each Object.keys(warning[version]).filter((section) => section !== 'date') as section}
								<div class="">
									<!-- ADDED -->
									<div
										class="font-semibold uppercase text-xs
									{section === 'added'
											? 'text-white bg-blue-600'
											: section === 'fixed'
												? 'text-white bg-green-600'
												: section === 'changed'
													? 'text-white bg-yellow-600'
													: section === 'removed'
														? 'text-white bg-red-600'
														: section === 'tip'
															? 'text-white bg-amber-500'
															: section === 'note'
																? 'text-white bg-purple-600'
																: section === 'top tip'
																	? 'text-white bg-orange-500'
																	: section === 'warning'
																		? 'text-white bg-red-500'
																		: section === 'info'
																			? 'text-white bg-blue-500'
																			: section === 'feature'
																				? 'text-white bg-teal-600'
																				: 'text-white bg-gray-600'}  
											w-fit px-3 rounded-full my-2.5"
									>
										{section}
									</div>
									<!-- END -->

									<div class="my-2.5 px-1.5">
										{#each Object.keys(warning[version][section]) as item}
											<div class="text-sm mb-2">
												<div class="font-semibold uppercase">
													{warning[version][section][item].title}
												</div>
												<div class="mb-2 mt-1">{warning[version][section][item].content}</div>
											</div>
										{/each}
									</div>
								</div>
							{/each}
						</div>
					{/each}
				{/if}
			</div>
		</div>
		<div class="flex justify-end pt-3 text-sm font-medium">
			<button
				on:click={async () => {
					localStorage.version = $config.version;
					await settings.set({ ...$settings, ...{ version: $config.version } });
					await updateUserSettings(localStorage.token, { ui: $settings });
					show = false;
					dispatch('confirm');
				}}
				class="px-3.5 py-1.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full"
			>
				<span class="relative">{$i18n.t("Okay, I'll be careful")} 🤓 </span>
			</button>
		</div>
	</div>
</Modal>
