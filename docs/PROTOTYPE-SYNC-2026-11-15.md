# Prototype → repository sync, 15 November 2026

This branch brings `src/ca-website.html` up to the review copy (claude.ai artifact "CA Website Prototype", version 1794709127-1325), with:

- Mujib's marked phone sheet (Work tiles, list entries and the top tile framed on phones to his yellow boxes, with the pictures he pasted in; published to the review copy on 14 November);
- every other review-copy change since this repository's last sync;
- IBM Plex Mono review, item A (approved 15 November): the arrows ← → ↔ ↕ ↖ ↗ ↘ ↙ added inside the three IBM Plex Mono Latin files, from IBM Plex Mono 2.005 (SIL Open Font License); every other letter unchanged;
- `public/fonts/ca-fonts.css` and its 14 font files, which the source now loads (the older `fonts.css` and its files are left in place, unused);
- 102 pictures and films checked byte for byte against the review copy.

## Added from the studio PC (15 November 2026, second commit)

- 50 drawings from `Downloads\dwg std\Cleaned` (the "web copy" files). With the C2PA content-credentials block that the PC copies carry taken out, each is byte for byte the review copy's file.
- 9 films from the review copy (each under 4 MB), byte for byte.
- 12 films from `Downloads\CA Website Masters\Live films (full quality)`. These are the studio's full-quality 1080p encodes of the same cuts (running times match the review copy's films and this repository's older copies), not the review copy's lighter encodes:

  - `vid/alpha-film.mp4`
  - `vid/alpha-walkthrough.mp4`
  - `vid/bgrt-hero-1080.mp4`
  - `vid/cascadia-walkthrough.mp4`
  - `vid/cross50-film.mp4`
  - `vid/cross50-teaser-1080.mp4`
  - `vid/mezban-film-orig-1080.mp4`
  - `vid/parallel-film.mp4`
  - `vid/rasa-prototype-1080.mp4`
  - `vid/sandyhook-film.mp4`
  - `vid/sandyhook-home.mp4`
  - `vid/unity-film-v2.mp4`

## Still to add before this can be built

229 pictures of the review copy (36.0 MB) are not on the studio PC as web copies and could not be taken out of the review copy in this session. Where the repository already has a file of the same name it is an older version; where it has none, the build's "a picture or film is missing" check will fail until it is added. Each line gives the path, the size and the SHA-256 of the review copy's version.

| Path | In repo now | Size | SHA-256 (review copy) |
|---|---|---|---|
| `img/alpha/s06.webp` | no | 60,196 | `6f1361514c4619b97e05f7563f651263ea577d6f09e13363a6f8d7a29bcc7557` |
| `img/alpha/sketches.webp` | older copy | 185,680 | `0a5318b3b93a3c5e2ab14b26f6418b841d4468fe3c779a887ebaf2469fdb30e9` |
| `img/barn/p03.webp` | older copy | 392,856 | `f56ccbafa9de24de36c12b42d2d4365ad9beeed7f9575a82ce8fa64b229459af` |
| `img/barn/p05.webp` | older copy | 332,674 | `7a4b688c27acc50d4704bcc3e519ea899f0668c4b76f644903334ca391d446fd` |
| `img/barn/p06.webp` | older copy | 373,838 | `1fdfd6983a58a4e434415647451c23411dc281f6368dc8a3dd2db469b62df965` |
| `img/barn/p09.webp` | no | 609,926 | `3dc4c59c889710fe933c7cfb8d0fa33c45981a38b653f6501036f951a16c20fe` |
| `img/barn/s01.webp` | no | 37,072 | `22590d06c702cdd7423d7fc6bb7f0a08b5d7c0c838234845f901299d9c00d1b9` |
| `img/bgrt/f01.webp` | no | 282,060 | `f750214883343cfcfea9be3c33ff2b1a69fa4788f124527871b96ce21548391f` |
| `img/bgrt/p01.webp` | older copy | 192,322 | `52676d328ae6abcc3ce7ae8d2132f0b7a8bdeb30463224afff54b06297e029c8` |
| `img/bgrt/p02.webp` | older copy | 140,122 | `a24ceacdaf7c3a63643673121d0af43a7738385e9638f8447943a755e68843c1` |
| `img/bgrt/p03.webp` | older copy | 118,566 | `402654e6b897aa33efe68ac5939f7ffd0811d4b1271ec46b7b45b9a11d6e4ee8` |
| `img/bgrt/p04.webp` | older copy | 87,298 | `56efddd0c1a12c28f0672988d958f4043910b179fe0fe2ef04cd386874ab49c5` |
| `img/bgrt/p06.webp` | older copy | 112,390 | `4a58a594df4d577e140f4cbc92e870d4ce88eaee8c8fa225bedbe4ab58e7b5c7` |
| `img/bgrt/p07.webp` | older copy | 144,470 | `570a1a70f046b243db328d54189163690c0b023d0d81dd4cdef4ac84bce5ad99` |
| `img/bgrt/p08.webp` | older copy | 167,314 | `a1482547c25f27e2b1ce023e6121f2f56a9907cdceb6feb4c25bcea19a3478b1` |
| `img/bgrt/p13.webp` | older copy | 135,962 | `18ab7363c2a3c96ab1cde5f85e4fa8aa8de73735a91c25484a7b2bea935e58a2` |
| `img/bgrt/p14.webp` | older copy | 132,466 | `b498eb0f7827256eeb05b4ea3659802fe4829cf5db619ace6d84a37e5312ee2b` |
| `img/bgrt/p15.webp` | older copy | 153,068 | `9c4b4dafa78a9e70085658f04c82d47460291c61bef54fe69e3889f2a7f89486` |
| `img/bgrt/p18.webp` | no | 151,822 | `66f615dc72b3b9e08116716fc5bb418397c1f2df5e15a6ef9d9272508b3a8793` |
| `img/bgrt/p19.webp` | no | 196,452 | `a905e93309e74108d1fd779b00cde3400bcebcdaa23294ae1b089b74a0f929a8` |
| `img/bgrt/p20.webp` | no | 170,120 | `ae8e44620fb6aa5c28a5b46bbb4d7ceec4b6702e7853a908074dc975c0d088e6` |
| `img/bgrt/p21.webp` | no | 213,098 | `b6cf312cb2c6c1faac467a6a60bcd1c0b2da50e48c92d1e921899023c40fd314` |
| `img/bgrt/sketches.webp` | older copy | 108,772 | `82bb235002e4a089274e627045614763fc20213879751a80fd597118c88d45cc` |
| `img/bgrtm/s01.webp` | no | 46,966 | `b93821b1b43d52b27f97315124023ca0e3ea9d7ac802972921e8ab11e5640135` |
| `img/brick/p01.webp` | no | 255,006 | `cd36b527cff7390c7f3a8dee5b326988585e7e29fedce84e582c23a0a8bf8f37` |
| `img/cantilevers/p01.webp` | older copy | 195,486 | `295c400ea1107e56fe4d4ebf40dc06c6f25e99378fa6c6686aa5f7a1bd90fc1a` |
| `img/cantilevers/p02.webp` | older copy | 169,300 | `a7ab5f159de4a8da7989d0ce06cc4a3aa5343826d050e341f1e8fd6dd93ffc69` |
| `img/cantilevers/p06.webp` | older copy | 319,068 | `7a4434123709739c0b37a3147f42a4cffb65564a6fe3ee05d435158c67ff1bd0` |
| `img/cascadia/s01.webp` | no | 38,616 | `db24766a82028091425182551e50d073270810e775dbe6f0cebc9ccd92d87e81` |
| `img/cascadia/s02.webp` | no | 196,550 | `7c5184498701c01aa2231bf492109fc3b31df9d4cead610bcf68db739ead7e5d` |
| `img/cascadia/s03.webp` | no | 31,352 | `5b7ae15f8854a2f605af64d7153d949a862c44fd9add5727c2289fd55dd42c83` |
| `img/cascadia/sketches.webp` | older copy | 66,520 | `ef44007f4f87cdeb6718e0538dfdba99330451a0639972127e5bf393d7010b22` |
| `img/cov/cv-designingpeace.webp` | no | 92,880 | `31a78b15c1bfa407b938637746e401d1e4677047c2a263dbca1b50bb6d7fbd02` |
| `img/cov/cv-ifj2026.webp` | no | 18,878 | `90eb4c9284d9efe66fc85d989eb140628884e7b8cf8b5d1a9b70cdac06162a50` |
| `img/cov/fairememoire.webp` | no | 11,780 | `7b4964c3c122361600756a2a241650bca83c79e993f65b8e7ccdc85d48bce6dd` |
| `img/diyar/p02.webp` | older copy | 161,636 | `4c874a092ff3bc4ccff85aa720e2efb5c5ae324ce136f86104702c4aa7f826fd` |
| `img/diyar/p03.webp` | older copy | 145,360 | `2090362fdc4be89070c154778230e1747d5abf8f3b10f8cd320bde9e1c9fe8bc` |
| `img/diyar/p04.webp` | older copy | 236,820 | `06ebed88367247b5088908c3f880a231cb81bb730f6f3df181a908230a1d57fd` |
| `img/diyar/sketches.webp` | older copy | 82,776 | `6028c8c4357998a0e2fa9f652b0306306e293e47f71e2e8e25036168128c0d85` |
| `img/jdt/p01.webp` | older copy | 168,246 | `d36a4cec0068075c55ba538ebe8a990efb3605e0028df99f761a25d3e9aa10fc` |
| `img/jdt/p02.webp` | older copy | 264,542 | `5cabda192ad29514c75b37df07d064d84e30e09a98a58c803c7489854b0137de` |
| `img/jdt/p03.webp` | older copy | 133,114 | `00cee49c5542dfb61abaaf789dcd27f813dd1da0ebbaea99579517fae4c351f6` |
| `img/jdt/p04.webp` | older copy | 139,338 | `73885da958a5d757d835f129aee76fb456b3e1e8f1bc347714d3552bd3574a58` |
| `img/jdt/p05.webp` | older copy | 142,862 | `b5c25ddd38bc6cf2bf61eeed9fe30ba6a82662f47a3eca443f9580b7c228a88c` |
| `img/jdt/p06.webp` | older copy | 67,330 | `f5b52407f5c9b7cd67c23028327fca8e7d740284c3393e5bb77dbf95d32a719a` |
| `img/jdt/p07.webp` | older copy | 130,370 | `e81779f7b5aefd80e12db07ad4c936f836e2517f23869a096a2c91653b5edc27` |
| `img/jdt/p15.webp` | no | 121,966 | `33ebf103ff2eacf409885cb89861c891a621336ba2ad7c77c156f3c698447913` |
| `img/jdt/p16.webp` | no | 64,808 | `50b793fc208baa4ae0d116c043ca1240d818aac63171e1ab3789caa9c934a75c` |
| `img/legend/d01.webp` | no | 82,098 | `d24e4cc8d309b05906f386c6d5df57fb5087b15f9ac941ac04c20f0c8281d469` |
| `img/mezban/p01.webp` | older copy | 88,502 | `cb93ed87b15bd39c40ab44d014f9d37df759e1b85d313faf398861d2109f791f` |
| `img/mezban/p02.webp` | older copy | 75,100 | `bb3c493a76d12f16170edff59626da37f206e84c85e59cb709087203953bb928` |
| `img/mezban/p03.webp` | older copy | 109,510 | `74e120e7181b6a918868902204874d5be2c91a26bbe8a512797350925461ebad` |
| `img/mezban/p04.webp` | older copy | 99,432 | `50eb00585445665b21270b3fd4fa37bd8bfe87bbb95f070fc3e6991543a5b90f` |
| `img/mezban/p05.webp` | older copy | 103,286 | `5644e52065f4c2adef5f649cac54966b190013c69457f2b3ef06575dfd58296f` |
| `img/mezban/p07.webp` | older copy | 64,946 | `431981f8622a46eff13d93eb73b1cef1c80986b33f73798eaa9613a09a6c737a` |
| `img/mezban/p08.webp` | older copy | 40,468 | `0952aa381faaa81baf9373515fe6971e7a923482030e02e2d2a4fdbd897687e4` |
| `img/mezban/p09.webp` | older copy | 76,068 | `88e7bcd2df7c4ef7cc10a23af49d10ae37303b12d587bd61a80d930be1ab93c4` |
| `img/mezban/p10.webp` | older copy | 92,426 | `d680a5fc937f6f6033fbc2c54e9f6e23403316879c4622ccee926db8fb5232a8` |
| `img/mezban/p12.webp` | older copy | 104,772 | `eb1b4e8234c3035be1af638538ff913c34b29fde43440dd966e8729c38369464` |
| `img/millerknoll/p10.webp` | no | 545,056 | `c32b7468db01d168c8ca55a3a3ea4cd2afd176c08df5e3d151bba84c5d5750d5` |
| `img/mosque/d01.webp` | older copy | 211,926 | `5327883e8c897e4cc7c862e3e5452f2e2224c097fc5e5cd6dc96e863cd636b8e` |
| `img/mosque/d02.webp` | no | 106,670 | `38508ababe391a1c60e01b8b503c11cab40c7dfec9f445e9d72c38dc35a98e64` |
| `img/mosque/d03.webp` | no | 153,574 | `3bc6264145c01374363d3612f6c620da6b800c26c864664ff77167c4b89c482b` |
| `img/mosque/d04.webp` | no | 53,344 | `98e92d8a9d93e6bafb46c020291ae97329eeae2106128fd63e51bf3bb05892c0` |
| `img/mosque/d05.webp` | no | 99,894 | `28b8826a7b22dac82deb2e442f8c570df23e97defbbdf236ce8df9237e8f1f60` |
| `img/mosque/p01.webp` | older copy | 74,364 | `ec22023aa7a870a959c98d5169b3d4bdaa0b2ef31afcfc7a8dece294e8540a47` |
| `img/mosque/p02.webp` | older copy | 140,016 | `6041841478ab0b8140deac748bafa63662df9f76b49750fc9c77f5c38572c8d8` |
| `img/mosque/p03.webp` | older copy | 204,724 | `52178cc21d9edaa19bd28216af3c1c1caf8aa90c32fe9b1d705335bdc301ce0d` |
| `img/mosque/p05.webp` | older copy | 113,608 | `5bb43b6bf58e439b28dd7463575b114588341f84fd78a66754b576d900a56f23` |
| `img/mosque/s01a.webp` | older copy | 89,036 | `49bbe1ba095b930f31e0aa9a042265c7b9040d18e0830992dc79d81617d94a6e` |
| `img/mosque/s01c.webp` | older copy | 68,284 | `24e33a6127e52583081422e0d7753d8ab1f0ef7599ca59b65f59e589c67a6864` |
| `img/mosque/s01d.webp` | older copy | 58,864 | `71a556559d2924af02e16bfcecf6aca90149f162f9ff05e72eab1f12e4a54028` |
| `img/mosque/sketches.webp` | older copy | 90,246 | `388750d2592939caf860193405ed2eee3d7a908fdf41a18a4e57285d93816389` |
| `img/musi/d01.webp` | no | 136,790 | `e86bf41f6d6b88a1bc0b0b26d2822c70b9b0b2b4c6de4245044378103a152b5f` |
| `img/musi/d02.webp` | no | 122,954 | `1d8cabe0417268db978fa5090df95ba990e238bc300647c265fded9f8124361d` |
| `img/musi/d03.webp` | no | 104,236 | `bb3a7f6a5d981485b9c857c8812499915a6483f1901c08c66424b51a27239e92` |
| `img/musi/d04.webp` | no | 143,582 | `6ff42b97af2783b8950401c3f464bf59f7bfe77efcfbeb88ba7cb351d1da75fe` |
| `img/musi/d05.webp` | no | 127,962 | `bb154a6395aa5411dda33e5b02d1e411fd8fc0892580c5cca1a0d690a05e88fc` |
| `img/musi/d06.webp` | no | 242,598 | `edfbfa333b669c460e54787daf14de4327a3354049c959798a419bcfe6170dee` |
| `img/musi/d07.webp` | no | 253,890 | `5951dd4dced0dd47d0fdcc14447eadac20d9f8e635a6d71dc76bd2d1b11fe92c` |
| `img/musi/d08.webp` | no | 305,208 | `320c240459152133e2d052653161d50864423a75a8cd8832ac92d89b8a4c7f28` |
| `img/musi/d09.webp` | no | 111,808 | `6b82ef8a9b171543ca18ba602be7eeb986c090945b4c229b25ed50652001fd2c` |
| `img/musi/d10.webp` | no | 214,290 | `5f5b2d968e7e4b2af94a6c65f250c1f9bc47fffa42fa178e7d8a4f2d6c9a1027` |
| `img/musi/d11.webp` | no | 310,120 | `81d43dd69cc44eae01bd70c6bc6f974c30d6114f1ed4c13d7af21a2fbdb65bb0` |
| `img/musi/p02.webp` | no | 241,230 | `a4a3143fdaeee1c4b500187ee84f9367f33f3f09c7230585b78c231b82dd8dde` |
| `img/musi/p03.webp` | no | 424,412 | `b98b969c28e7cf6d13d7b9d20f4d7ee9099a1bcf3474f22deaa8b5b3e833b1ff` |
| `img/musi/p04.webp` | no | 200,416 | `b5562f915a0aa58ef65e252ae36d8c0827f4ecd87d6c945469c845bb81e3a9b2` |
| `img/non/d01.webp` | no | 28,500 | `b778bf48eeb26d096de88a7a4aad1b64f1487143ef54f31601140a4192782fb1` |
| `img/non/p01.webp` | older copy | 130,658 | `384e7b08e280806050b4233f7d6a52a93ffbb428468605eece9fec4c1fe98e0b` |
| `img/non/p02.webp` | older copy | 226,606 | `88990bfc182f53585327324d1d22b48bc96a573bf9e362224d14998528e9bc26` |
| `img/non/p03.webp` | older copy | 121,092 | `3e2edc4d8a6e195788d797454bb1d9a6d4cd6a368d24700ce1baa21779ebffa6` |
| `img/non/s01.webp` | no | 114,022 | `10ad5bf7e4ee6feed1d01bec27fd905fb71dd9a378fee5855ddabcc945fcbcfb` |
| `img/parallel/p03.webp` | no | 131,678 | `c6579bced0c4507c8c4ebecaba21414b4519972c866bf1ce37dee9f2e815993f` |
| `img/parallel/s01.webp` | no | 195,722 | `e659b3608580cfc8010b0b213c0e0df87c5eee059ef743dd946cc7f20d709b9c` |
| `img/peace/p04.webp` | older copy | 511,442 | `faf6a33d571d18b3b15383ddc5580aaa1b5c7603f0e6c616c1639f651ecafa86` |
| `img/rasa/p01.webp` | older copy | 277,892 | `a480ad6d3199f0366fa60e164a6411c9584ed49f122e78ed69c1ddb1e657935b` |
| `img/rasa/p04.webp` | older copy | 257,468 | `884a151781eee4756cf89cc5958fd1ea41dc41b6a72c5d9ec838b71a5038ab47` |
| `img/rasa/p05.webp` | older copy | 197,316 | `4e88cd16acba556d73bd4c5972de36aa8b8ee32c29dcd64447d6485798b8e5b3` |
| `img/rasa/p06.webp` | no | 267,660 | `b3e8a6a8eb7c66961789c085376dbad868a6ed002cdc350aa77016e679180fb5` |
| `img/rasa/p07.webp` | no | 175,566 | `8a28158e567b8974c1af51e6eda7863522cf199c7cab3f38b906d3edd5cf18a6` |
| `img/rasa/p08.webp` | no | 164,932 | `2f1a8d16832d33559190911d983d5e876ca1ef93f68a4ae3616f3d8cdb0b4662` |
| `img/rasa/p09.webp` | no | 256,484 | `882fd221b9a5a41e52ba30467a3acdc56ca21699d3431b5838563c37be0e56ed` |
| `img/rasa/p10.webp` | no | 128,914 | `56396aac30832bb067380f1dcddff2c1180a6717f9fb9d497ddce7e67c92a2d5` |
| `img/rasa/p11.webp` | no | 139,508 | `6664617bcc53011196ea7d579e9df1623f7d1622c7f5fcbe4045bb227b7ebf2d` |
| `img/rasa/p12.webp` | no | 237,154 | `b0d78b8b80415c5a96af8ad7adb26630b7f4f9949ddaed063c708a54326c2e59` |
| `img/rasa/p13.webp` | no | 186,242 | `e38803450f01bea3d7d30195aa06b7de9cc48173b116133620b2146eca921670` |
| `img/rasa/p14.webp` | no | 189,786 | `dc8f15fe5b77cb0e355ad4d70dc5ebb38f5c989919722d47d87ff7acc6249384` |
| `img/sandyhook/f01.webp` | no | 329,944 | `a8aa4eb6f82f3743076359cafa55122f917b72781133dbb47193b2ae8c1fee55` |
| `img/sandyhook/p02.webp` | older copy | 250,660 | `734099b70f80006eedc4206b531964887f6f8d2aa396801a1f45447eeee68143` |
| `img/sandyhook/p03.webp` | older copy | 228,908 | `7f9099f8efe28c77d7115ca1751946278e4f30031817c3bb42e4d50cb6607dc7` |
| `img/sandyhook/p04.webp` | older copy | 119,488 | `490ce39e3d3d0a2a38df91a50e70acca31b4c3389e22699c45210469d5c14167` |
| `img/sandyhook/s01.webp` | no | 151,670 | `5b0ffc0c49714be241814e218b2c876f123c1b8ce3950926509c75748fa2caeb` |
| `img/sandyhook/s02.webp` | no | 158,762 | `e816a388eb96e7784d7287fa0fb31d1dce53f21cd9f62b33f14e9fd17d26d638` |
| `img/sandyhook/sketches.webp` | older copy | 82,252 | `8c429c0a688f8e891352c7c6e5b26b278c01a90e8b7fbcd5af3f5a4d0a7db1e4` |
| `img/shoah/d02.webp` | older copy | 206,216 | `25a81bd6df78a2224a091a0d0ff30ae52814ce0d4618b3e724ad8075e2bedd12` |
| `img/shoah/d03.webp` | no | 630,070 | `f48a7fae751b49118b5e0e296433445c69a5fbe2f66d3af252be60eb2ce2a9e2` |
| `img/shoah/d04.webp` | no | 144,566 | `0e988a1478d0b7038f879dacdc877c5b27a3bb46c8dd81ea0a083eba08060909` |
| `img/shoah/p02.webp` | older copy | 455,628 | `18db5fe4b95beef14ffba3bb85fdf584bf82205a14ea3a8dfa784189b9b880e5` |
| `img/shoah/p03.webp` | older copy | 475,646 | `e7e3bb4fd8eec34e1a264b311fe6cc28fd7b9eab8e9dc0bad320e70f54b196e5` |
| `img/souk/d01.webp` | no | 285,232 | `d8dabe45ed18895d88fac485d152a3e8f418e1fcba843678907ef5a16a1a45d2` |
| `img/souk/p01.webp` | older copy | 379,236 | `f5e732c45871b3c10c6cc51c7d1abe19662dcdeea57b1f977ecad668f60592d7` |
| `img/souk/p02.webp` | older copy | 162,318 | `3d97991d48a25e7111a6ce4346f62352ea94d344a9c3699ea723f9b935c79851` |
| `img/souk/p03.webp` | older copy | 247,722 | `d94996ac2419c43c1fa60af0706c149cbae88926d227e5b657b41ca1700036a1` |
| `img/souk/p04.webp` | older copy | 141,366 | `dcd1ccab099862e21ca4f7cd194c95c6eb9e7e5e725c845d3a1389a90f5470c3` |
| `img/souk/p08c.webp` | older copy | 172,112 | `eba36f2501eb7d702ecfd82fa7cfff21a793884f3103cf3b6620df3b805ad1e9` |
| `img/souk/p08d.webp` | older copy | 155,326 | `8a3ec28bda5a828b04dcdd6445bba73a2a08a3df7c335a2b4208d4a34869b4a5` |
| `img/souk/p10b.webp` | older copy | 88,360 | `e4d30d99c086b5c6d5e652a4312d0b226ae63efe9781c4aa3ebe26fc88d1e89f` |
| `img/souk/sketches.webp` | older copy | 51,220 | `124b382ac10cdd432ae38cb0881a581f2fa8fe1f91665ec6f3aa19de59c7c308` |
| `img/spicy/p01.webp` | no | 239,202 | `94ba613590fa02f4e501599fc50c0e456c4f5922129e11fd06047aceab3ae889` |
| `img/spicy/p02.webp` | no | 167,532 | `2ef767a7f19f09af102ca1bc3dfe01fd7da802b7b2b2a7196a3dda02d594a494` |
| `img/spicy/p03.webp` | no | 164,388 | `d340e68c826bc89e292c0e065378745259853027d974c50f7e97dd9d642398c7` |
| `img/spicy/p04.webp` | no | 296,542 | `899f5ee0879251652ed8f3673848be316071594c9eb0726c6b8d14ba7d4337e2` |
| `img/spicy/p05.webp` | no | 178,230 | `158d4120c100c52d9a514fb0984c6e39acbed6be9c55468dc924ae7cefebcc47` |
| `img/spicy/p06.webp` | no | 134,548 | `31e47ff3f3eaff09728ee1e1999a142a8f9be20087119a029fc921c6567ba678` |
| `img/stanley/p02.webp` | older copy | 282,322 | `d75f41fc471a497ef320401ea730ed7944413dee2d15b550573282c20a95f62e` |
| `img/stanley/p03.webp` | older copy | 122,804 | `cc630d7c2543b28d173616808dcab761e1db2c88f4027883d635a2b377329857` |
| `img/stanley/p04.webp` | older copy | 320,640 | `a2fe787b46f3101c34133616b81479917118285142cf28d5292adfef136e4cf4` |
| `img/stanley/p05.webp` | older copy | 120,624 | `672fd22e6fc1351d99dbc6fe473b691c42ef8df0f886b8e5fb144eae79e0c4ea` |
| `img/stanley/p06.webp` | older copy | 117,224 | `ba70aafe50cc73702456c98015cb78f6e0b9c9724a4fab40540a83f66ecd4eba` |
| `img/stanley/p07.webp` | older copy | 129,484 | `bfd76878157893681f43fbf5d9b786af505c4952676593527fd2c45f49c44fbd` |
| `img/stanley/p08.webp` | older copy | 178,554 | `0008600b0cc96a4ad35ae87359445b26317e594f52688a1d8f305d3983927ee0` |
| `img/stanley/p09.webp` | older copy | 385,834 | `7363f753268c9749670c768f5a9f73119b805d9e946bf823035c2769f84e2b57` |
| `img/stanley/p10.webp` | older copy | 108,398 | `ecf75bb10d9845710be655c99c804dfea7156cd29b6544e837cc5d2cf27e0e9c` |
| `img/stanley/p11.webp` | older copy | 105,872 | `6d9980e37e3fe3e2b60bd1239900778314633735632792b962ce5f3f070ee8b1` |
| `img/titan/p01.webp` | no | 165,176 | `ec7af50025a139002aef304feebc9ae56230aba7fd5c407046413294f0ef0c20` |
| `img/titan/p02.webp` | no | 259,860 | `115a68f0f47078ee780a79c827afe7a0f706878d3aedb22caa740acd03a65846` |
| `img/titan/p03.webp` | no | 142,662 | `ee1384ca39d9e52438a2610a5e210806436b7d040d5795dcc583d469844f45a1` |
| `img/titan/p04.webp` | no | 260,034 | `ef9f026cc93c361e6a4f89c8be46f0e17d3dbbb8b8e49ebdca7a18dbf325ae8c` |
| `img/titan/p05.webp` | no | 138,352 | `28bf84b3fcbc14baffd7f3f8403440b4948e7ca4ea0d260837ab46920779adbf` |
| `img/titan/p06.webp` | no | 100,262 | `52689aafdad5ba4ed167b268baee7db2b3308f67791a70b1212f5f2757781f1b` |
| `img/titan/p07.webp` | no | 90,978 | `72e979a6efcee9924afe53f2dd1b76b4101349eec8ec71fc9d176ca4b11c6197` |
| `img/titan/s01.webp` | no | 81,696 | `8553b6b63aafb9d5ec0090793d5ed4e5d6076e92093f0efea64ef2d82f369d47` |
| `img/uae/p01.webp` | older copy | 164,172 | `7a4488b0952187a879581e96e6e66044e6d080a868d38aaf06a262ac689e035a` |
| `img/uae/p02.webp` | older copy | 103,180 | `5d7550bd198086a680c1ee1256f3edfbeb7f02fcf3439168ba00df36e53f51ba` |
| `img/uae/p04.webp` | older copy | 172,562 | `e8aeb3a9be3bc908592e12e246e4a859b63e6071006724d26b30589f0b5a56c7` |
| `img/uae/p05.webp` | older copy | 114,892 | `831c02ff842c11b2f6a7f4bf3b9a4de3296f29e853299ec07f0748b6d4a097f1` |
| `img/uae/sketches.webp` | older copy | 153,254 | `246cf44f51d02cfede59914c3370d83d88e832d31fc2251384fb6e3565b7f1c5` |
| `img/unity/p01.webp` | older copy | 204,296 | `c84778d4aa07d5bcbed74cf96a07e4b6677a74e93460a131f44828877a2aef75` |
| `img/unity/p02.webp` | older copy | 100,972 | `f65d2141b7677f9b0dde7bbb4fc3f6dbe19380023909c7fc406138a643a2aa74` |
| `img/unity/p03.webp` | older copy | 228,526 | `ab7bb924c35a08690371a4b194d777f0435576ad8c3dda170910f087288953e2` |
| `img/unity/p04.webp` | older copy | 199,118 | `43bf378444cf27e0664486c41ef503fd86fbfaf5f397f714ff266584484cc145` |
| `img/unity/p05.webp` | older copy | 168,740 | `b329aaa00782b9d021793fec11fddf9120f8faa1705bbbf750819fbdeed2a33e` |
| `img/unity/p06.webp` | older copy | 74,006 | `fbed8c20493ddc60ee81b0a84ac86104574261465488732d3fc33510aaa2d011` |
| `img/unity/p07.webp` | older copy | 95,476 | `8c87af0582aa0f00691f7f7580d0bf1519aa1ab045b9b704c478564615869c50` |
| `img/unity/p08.webp` | older copy | 165,424 | `30b4a2873c66159fc82f6ee7924ac4ee76d8eea24286cbd76e039eede95f56a1` |
| `img/unity/p09.webp` | older copy | 167,434 | `d88bb88135687aa208259aad3a9a02858512a635b859571deb6d0c12eb0857c6` |
| `img/unity/p10.webp` | older copy | 232,426 | `4f41751fb0cffb96aa4d06573ec56df0f105eebfa9fd432a9e0594493cec9533` |
| `img/unity/p11.webp` | older copy | 214,792 | `711cfc970a0276742dea2aa961208c6fc233c1b2dbbd5949eede326ec3a6b952` |
| `img/unity/p12.webp` | no | 147,514 | `708bb7b63a83dea60e4aa2ef279d6cf63704d59b945c65e9ed7c689f119587c6` |
| `img/unity/p13.webp` | no | 172,072 | `1f7d2d4ebe05d4b5f17d616fb368d80140a4e67ec6b92e9fae4ae51efe511199` |
| `img/unity/syms.webp` | older copy | 164,658 | `08a3a951a7de8fa43d5e3f995e2d46f6630765bf9d44a0c8531f5c599a6add86` |
| `img/urnes/p01.webp` | older copy | 388,476 | `58d24c3b989bf64ca752787292ae64725526ba89b25efa35f9064900b0af5cbb` |
| `img/urnes/p02.webp` | older copy | 433,874 | `4eab2f82edb3bd7e6cac3fb9d3fb4e0eeec0ecdcc618db314079dcd0ca9fde2f` |
| `img/urnes/p03.webp` | older copy | 397,798 | `3ed933416f98b040a97c13478649bddd79142a8bc7e125d6b87955aad18a4e03` |
| `img/urnes/p04.webp` | older copy | 425,442 | `c7c3097acf463ca140aa15be272e64253f3d0da2c0d122b477289d0d4c616b67` |
| `img/urnes/p06.webp` | older copy | 224,488 | `0469b5d2fe06009af0c23e2d16a3c0bc3c5c95ff3cae82b3070a9d2d950ccc79` |
| `img/urnes/p07.webp` | older copy | 107,006 | `81b3f5f2007af153dc768606ed3a69e2ea1fca2ef00a697e57dc33ba954d112f` |
| `img/urnes/p08.webp` | older copy | 169,564 | `aecdb6ec2bb843c8e2309307f189db7f7e86e74a5d1075debdbdfa6189d56497` |
| `img/urnes/sketches.webp` | older copy | 194,306 | `8cab1219340a2499fc9946672e0b0a2ed9db77654cb9e809bb667cc5cd01fa43` |
| `img/vessel/p01.webp` | older copy | 476,672 | `fde4d5982bfeac3c9b8a31a4b6403cf2e1a700ba0925c0424e44f9555992daf8` |
| `img/vessel/p02.webp` | older copy | 272,786 | `771256f205d9add9663514f253b77cf79ccbd33852b5978f5a3797a6e8e82350` |
| `img/vessel/p03.webp` | older copy | 403,632 | `82b9ad91e5c8a17d44200814d1c1de47dd2684de69a470750214b947c83f3b30` |
| `img/vessel/s01.webp` | no | 41,600 | `18c3505c62c77b43db06939a9fb915a04dfb7b948fe3aeadb49afcc2dbe52d58` |
| `img/wafira/s01.webp` | no | 100,186 | `6562375e6d9254429f2b25a6223611293a04666cd14aa302826e5cfb17d05412` |
| `img/wedge/p01.webp` | older copy | 140,264 | `57bf04f94f7ff56259a0f0c3cd45218fdba5f0098a8a1db3327a97b5fa813036` |
| `img/wedge/p05.webp` | older copy | 152,884 | `cdba235801e094ea59cb4498deb9e2e10567c0ca5411e1c0d7aae222826219a7` |
| `img/wedge/p06.webp` | older copy | 101,040 | `9f74497f74252c353a3701acb82d3444459a9c9ce937933002545ff001f8e8f4` |
| `img/wedge/p07.webp` | older copy | 95,180 | `40ec6a7f200d659673a3cbce1ba6bcc5a63712e52b546ad470be6787fa2b10d6` |
| `img/wedge/p09.webp` | older copy | 169,454 | `8a780594cad7c34e79e8201279614461597df3da26427eb40807b40f43a29404` |
| `img/wedge/p10.webp` | older copy | 50,934 | `270016aa0067fa4c94e7449e37d733743d69510118f7a04a6d10c3cdeb9ecc00` |
| `img/wedge/p11.webp` | older copy | 26,934 | `0ecf599ee35b43681e33fa22732202a9847d553f3f7ee49567617a889c650d7b` |
| `img/wedge/p12.webp` | older copy | 58,140 | `961b7e6270bb6eb975cebd327e876e1e062e45a0ce88647212ef49b08ed7e71c` |
| `img/wedge/p14.webp` | older copy | 27,322 | `bb5f371887c10c9ede06b9bb767799bbcd7d2fa601e1885e58f8befff6ddf1c3` |
| `img/wedge/p15.webp` | older copy | 45,974 | `4bfce3256deb927398ede4e6ffda6525ba2507df54142d7244c44dba4024a2e0` |
| `img/wedge/p18.webp` | older copy | 241,566 | `5bf8b0f6d926eb195a9d57fa8ec674920eb71c6183cf1c749f9e4728cffce765` |
| `img/wrap3/p02.webp` | older copy | 104,984 | `44ac6234876479cb387d9843dbf41e87a5c68124b6f42149d8057c37438c6a2e` |
| `img/wrap3/p03.webp` | older copy | 223,334 | `e9655770f0070441eaa63bcf682438b584251348e22df3b9b84b1ee3e360b3eb` |
| `img/wrap3/p04.webp` | older copy | 126,040 | `be77adc042867ea1d2615275409f7ffd0ad40b00a71c6dd0f9c624cfe20867cc` |
| `img/wrap3/p06.webp` | no | 74,308 | `8bfedf646b4f03275cf1f9dcdac4c6eb3bb556c2695cf12c24cf78136078ee34` |
| `img/wrap3/p07.webp` | no | 88,062 | `9ddd96688cc8a1a82d8e2e67af2e2a9ee66b105b769ebeff8f79e7ccab84956e` |
| `img/wrap3/p08.webp` | no | 79,220 | `38acb31f901f1240e49a5369d81f676ad0120aa2ee49dce48509b05e3f0a44ea` |
| `img/wrap3/p09.webp` | no | 136,648 | `f1f5fcfa92fb4251e3f8ddc35f5816316cab92b9dd0829630746b59e0be1d890` |
| `img/wrap3/p10.webp` | no | 130,522 | `357ada75c20280b5011f719962ff34886897ee0c61a50140f7999c1c875fab2f` |
| `img/wrap3/p11.webp` | no | 94,444 | `347887c3aaba7632205411031630bc26c262935273053716fe77f1e4403b7689` |
| `img/wrap3/p12.webp` | no | 66,946 | `7f098d2a0b07b0ee6e517b0858f43412e2d69207bb7440d27890ecd3a087657e` |
| `img/wrap3/p13.webp` | no | 48,708 | `8bf5e349ede2979bc3a9d9ceaf849ce7738a5ed62bbe9c0d3a1c865c1dd7c6f0` |
| `img/wrap3/s02.webp` | no | 61,598 | `e0c00d6faf3c81439c0c5527899351a554cb53a3ceb521fe7f23049f85a02fca` |
| `img/wrap3/sketches.webp` | no | 53,426 | `3e21d2cb5fa0dfec9ddebac5695578627d617f64f6e295a279b1c2123942147e` |
| `img/wrap4/d01.webp` | no | 168,020 | `416dcddefd969bc871cfc723277713eb6ee93cfea3225a84a15a1a195f25ef9d` |
| `img/wrap4/p01.webp` | older copy | 119,030 | `42a33ba81dee2d734cbf215862ff5a5a517aba90b597c5edbde82b7aa7ef8e73` |
| `img/wrap4/p02.webp` | older copy | 111,178 | `f6252383644a1c298e96062730eeee676bd014e09d15c312ca4ec81d74231994` |
| `img/wrap4/p03.webp` | older copy | 103,954 | `3bf4c89c6990c6e139d86a25a7dbf7244e0ad7b955e1e803e1ce78f26f87229b` |
| `img/wrap4/p04.webp` | older copy | 77,174 | `2be1164fe8de2664e771b11f7c9ef8e4ee56ebe5d27e2c04e22ad2efe6f3b554` |
| `img/wrap4/p06.webp` | older copy | 74,992 | `7a6a11d84844d0f388f4e6361ce6253ba5cf5fd5f32169a741252cf1ad6586c3` |
| `img/wrap4/p07.webp` | older copy | 105,750 | `98fe4a47dfa8fdaaf51a5c154e37e7a5456eec1fd95f474c21ad99cdb1dc8c51` |
| `img/wrap4/p08.webp` | older copy | 82,632 | `8d562974337d8eeaf52a118792854e47175ec13a92fffb338ab8e510599b5e1d` |
| `img/wrap4/p10.webp` | older copy | 72,468 | `86fb0d98c6ea8474ae51ec5eb28e0939fcdb61c37bfbfd2c9facb2f36517a89c` |
| `img/wrap4/p11.webp` | older copy | 55,028 | `c317d5fc4b104a3e9007968a67635c42b4a5a925f36326a62363a84ae18da80b` |
| `img/wrap4/p12.webp` | older copy | 40,720 | `ecc5e1331e53701e7b25f230e5984bea4ffc2a054b8a435efbe21d2563bc1a15` |
| `img/wrap4/p15.webp` | older copy | 54,636 | `f9d7eeff7a08be9e52a7daf50bd5167f857b964b2542f7e8dd8c29f5a5567991` |
| `img/wrap4/p16.webp` | older copy | 41,530 | `81d6dfa39662343ef6231964a4849b62eef3590550463a4d581c9b1d0569f13d` |
| `img/wrap4/p17.webp` | no | 71,126 | `1fe5cfac347614c45431ac3aa1230fe2de9389e6df5dc630e531e39ff9a83227` |
| `vid/barn-transformation.webp` | no | 57,504 | `67f075cc791372117aa6aabfb26e1f4af707703b3c60e210b834491c2985a301` |
| `vid/cross50-film.webp` | older copy | 68,056 | `db95768df15fd5966210c04c0e92823bd38bdd2e18df66ac4b83c2a4971a21ec` |
| `vid/cross50-teaser.webp` | no | 96,626 | `6bc13c90bee4f488df2a907c2ca9458b195edcb278e91b15389a2ad313342abc` |
| `vid/diyar-gateway.webp` | no | 113,338 | `1c4a4d694aa0a276f30439717fd2bdccec4f9ca2efe1805b340f5d85740a05c0` |
| `vid/parallel-film.webp` | no | 139,124 | `339b72d73de7564c8c800df4dd2f493ae166381f55c1d9775d0dd78f7eb2f2ce` |
| `vid/unity-film-v2.webp` | no | 13,666 | `39334594be105c0560b11c8c9357b2c15de4af90ec3f328e11a35e7499532c91` |
| `vid/vessel-film.webp` | older copy | 155,552 | `344d12c6f4a4a592dd521cd882e4a563c59102449be798715ccbeab2afb98cd3` |
