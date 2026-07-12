CIRCUIT_FLOW = [
    {
        "type": "token",
        "data": "Welcome to your Moroccan adventure. I can help you find the perfect journey tailored to your interests. Below are our curated circuits, each offering a unique experience.\n\n### Imperial Cities Circuits \n Step back in time and walk in the footsteps of sultans. This circuit connects the four historic capitals of Morocco: Fez, Marrakesh, Meknes, and Rabat. Immerse yourself in the vibrant energy of ancient medinas, marvel at the intricate architecture of palaces and mosques, and get lost in bustling souks filled with spices, crafts, and timeless culture."
    },
    {
        "type": "circuit_link",
        "data": {
            "title": "Imperial Cities Circuit",
            "id": "imperial_cities"
        }
    },
    {
        "type": "token",
        "data": "\n\n### The Thousand Kasbahs Circuits \n Journey along the legendary \"Route of a Thousand Kasbahs.\" This path winds through dramatic desert landscapes, lush oases, and breathtaking river gorges. You'll discover iconic, centuries-old mud-brick fortresses (Kasbahs) that rise majestically from the earth, each telling a story of ancient caravans and powerful dynasties. It's the perfect choice for lovers of history and epic scenery."
    },
    {
        "type": "circuit_link",
        "data": {
            "title": "The Thousand Kasbahs Circuit",
            "id": "thousand_kasbahs"
        }
    },
    {
        "type": "token",
        "data": "\n\n### The Igoudars Circuits \n Venture off the beaten path to uncover one of Morocco's best-kept secrets. The *Igoudars* are fascinating and ancient fortified granaries, unique to the Amazigh culture of the Anti-Atlas mountains. This circuit is for the curious traveler looking to explore authentic heritage, stunning remote landscapes, and a piece of living history that few get to see."
    },
    {
        "type": "circuit_link",
        "data": {
            "title": "The Igoudars Circuit",
            "id": "igoudars"
        }
    },
    {
        "type": "token",
        "data": "\n\n### Southern Routes Circuit \n Embark on the ultimate Saharan adventure. This circuit takes you deep into the heart of southern Morocco, where the world opens up to vast desert landscapes and serene oases. Experience an unforgettable camel trek across majestic sand dunes, spend a night in a desert camp under a blanket of brilliant stars, and witness the raw, soul-stirring beauty of the Sahara."
    },
    {
        "type": "circuit_link",
        "data": {
            "title": "Southern Routes Circuit",
            "id": "southern_routes"
        }
    },
    {
        "type": "token",
        "data": "\n\n### Sporty Treks in the High Atlas \n Answer the call of the mountains! This circuit is designed for the active and adventurous traveler, offering challenging and rewarding treks through the stunning High Atlas range. You'll hike past remote Berber villages, cross dramatic mountain passes with breathtaking views, and experience the majestic nature of North Africa's highest peaks up close."
    },
    {
        "type": "circuit_link",
        "data": {
            "title": "Sporty Treks in the High Atlas",
            "id": "sporty_treks_high_atlas"
        }
    },
    {
        "type": "token",
        "data": "\n\nIf you would like more details on any of these circuits, just ask! "
    }
]


# In your Python service file

IMPERIAL_CITIES_FLOW = [
    {
        "type": "token",
        "data": "  "
    },
    {
        "type": "circuit_header",
        "data": {
            "title": "Imperial Cities Circuit",
            "id": "imperial_cities" 
        }
    },
    {
        "type": "token",
        "data": "Dive into a 7-day journey that will bring to life the past glories of Morocco's four historic capitals. Explore the labyrinthine medinas, sumptuous palaces, and iconic monuments of Fes, Marrakech, Meknes, and Rabat. A cultural circuit ideal for history and architecture enthusiasts."
    },
    {
        "type": "token",
        "data": "\n\nHere is the proposed timeline:\n\n"
    },
    {
        "type": "timeline_start"
    },
    {
        "type": "token",
        "data": (
            "**Day 1 - Arrival in Casablanca and transfer to Rabat**  \n"
            "Arrival at Casablanca airport. Transfer to Rabat. Check-in and free time to relax.\n\n"
            "**Day 2 - Rabat and Meknes**  \n"
            "Visit the administrative capital, Rabat: the Mausoleum of Mohammed V, the Hassan Tower, and the picturesque Kasbah of the Udayas. Departure for Meknes. In the afternoon, discover this UNESCO World Heritage city, with its magnificent Bab Mansour gate and the ruins of Moulay Ismail's granaries.\n\n"
            "**Day 3 - Fes, the Spiritual City**  \n"
            "Journey to Fes. Full day tour of Fes. Explore the world's oldest medina, its craft districts, its colorful souks, and the Bou Inania Madrasa.\n\n"
            "**Day 4 - Immersion in Fes**  \n"
            "Continue exploring Fes, including the famous tanneries, Seffarine Square (the coppersmiths' square), and historical monuments. Traditional dinner show in the evening for a complete cultural immersion.\n\n"
            "**Day 5 - The Journey to Marrakech**  \n"
            "Travel through the spectacular landscapes of the Middle Atlas and High Atlas mountains. Arrival in Marrakech at the end of the day. Settle into your riad and take a first free stroll through the city.\n\n"
            "**Day 6 - Marrakech, the Ochre City**  \n"
            "A day dedicated to visiting Marrakech. Discover the Bahia Palace, the Saadian Tombs, the iconic Koutoubia, and the Majorelle Garden. In the evening, immerse yourself in the unique atmosphere of Jemaa el-Fna square.\n\n"
            "**Day 7 - Adventure and Relaxation in Marrakech**  \n"
            "Free morning to explore the souks, go shopping. In the afternoon, a Moroccan cooking workshop or an optional excursion to the Agafay Desert. Farewell dinner in a traditional restaurant."
        )
    },
    {
        "type": "timeline_end"
    },
    {
        "type": "token",
        "data": "\n\nThis itinerary offers a perfect blend of history, culture, and adventure. "
    }
]

THOUSAND_KASBAHS_FLOW = [
    {
        "type": "token",
        "data": "  "
    },
    {
        "type": "circuit_header",
        "data": {
            "title": "The Route of a Thousand Kasbahs",
            "id": "thousand_kasbahs"
        }
    },
    {
        "type": "token",
        "data": "The Route of a Thousand Kasbahs is an iconic tourist itinerary that runs through southern Morocco, mainly along the Dadès and Draa valleys. Its evocative name refers to the exceptional density of kasbahs and ksours (fortified villages) that dot the route.\n\nThis circuit is not just a geographical journey; it's an immersion into the heart of the history and culture of southern Morocco. It offers a unique exploration of pre-Saharan architecture, characterized by impressive and elegant mud-brick (pisé) constructions, often adorned with Berber geometric motifs. The route follows the ancient caravan paths that once linked the Sahara to the north of the country, thus offering a perspective on the ancestral lifestyles of the Berber tribes who inhabited these regions.\n\nThe general concept is based on the idea of a journey back in time, where the arid and majestic landscape serves as a setting for earthen fortresses that bear witness to an era of tribal wars and flourishing trade. It is a route that highlights the resilience and architectural genius of man in the face of a hostile environment."
    },
    {
        "type": "token",
        "data": "\n\nHere is the proposed timeline:\n\n"
    },
    {
        "type": "timeline_start"
    },
    {
        "type": "token",
        "data": (
            "**Day 1 - Arrival in Marrakech and transfer to hotel** \n"
            "Arrival at Marrakech-Menara Airport (RAK). Transfer to your riad or other accommodation in the Marrakech medina. Check in and take your first exploration of Jemaa el-Fna Square.\n\n"
            "**Day 2 - To the Route of the Kasbahs and Ouarzazate** \n"
            "Depart from Marrakech in the morning. Travel through the peaks of the High Atlas, crossing the Tizi n'Tichka pass (2,260 m / 7,415 ft). Visit the ksar of Aït Benhaddou, a UNESCO World Heritage site. Arrive in Ouarzazate at the end of the day, the \"gateway to the desert.\" Check in and have dinner.\n\n"
            "**Day 3 - From Ouarzazate to the Dadès Valley** \n"
            "Visit Ouarzazate and the Kasbah of Taourirt. Continue the road towards the Skoura Palm Grove and the majestic Valley of Roses. In the afternoon, travel along the \"Route of a Thousand Kasbahs\" to reach the Dadès Valley. Check in and have dinner in a traditional kasbah.\n\n"
            "**Day 4 - The Gorges and the Draa Valley** \n"
            "Continue discovering the Dadès landscapes with the steep cliffs of the Todgha Gorges. Free time for a short hike. In the afternoon, drive to the Draa Valley, the largest palm grove in Morocco. Enjoy a traditional dinner show in the evening for a complete cultural immersion.\n\n"
            "**Day 5 - Adventure in the Sahara Desert** \n"
            "Travel along the immense Draa palm grove and its fortified ksour. Arrive in Merzouga, the gateway to the Erg Chebbi desert. A camel ride will take you to the camp. Spend the night in a Berber tent, under the starry sky of the Sahara.\n\n"
            "**Day 6 - Return to Marrakech** \n"
            "Early morning wake-up to admire the sunrise over the dunes. After breakfast, return by camel and depart by car. Long drive back to Marrakech, with stops at points of interest along the way. Arrive in Marrakech at the end of the day for a well-deserved rest.\n\n"
            "**Day 7 - Adventure and Relaxation in Marrakech** \n"
            "Free morning to explore the souks, go shopping, and discover Jemaa el-Fna Square. In the afternoon, a Moroccan cooking workshop or an optional excursion to the Agafay Desert. Farewell dinner in a traditional restaurant."
        )
    },
    {
        "type": "timeline_end"
    },
    {
        "type": "token",
        "data": "\n\nThis itinerary offers an unforgettable immersion into the landscapes and culture of southern Morocco. "
    }
]

IGOUDAR_CIRCUIT_FLOW = [
    {
        "type": "token",
        "data": "  "
    },
    {
        "type": "circuit_header",
        "data": {
            "title": "The Igoudar Circuit",
            "id": "igoudars"
        }
    },
    {
        "type": "token",
        "data": "The Igoudar Circuit is a tourist and cultural itinerary that focuses on the Chtouka Aït Baha region, located in the Anti-Atlas, in southern Morocco. Its name is derived from the Berber word *igoudar* (plural of *agadir*), which designates fortified collective granaries. These structures, true fortresses of stone and earth, once served as storage places for crops, valuable goods, and official documents of the tribes. They were also used as refuges in case of attack.\n\nThis circuit offers a deep immersion into the history, culture, and social organization of the Berber tribes of the region. Unlike the famous \"Route of a Thousand Kasbahs,\" which highlights lordly residences, the Igoudar circuit focuses on community-based architecture, revealing the solidarity and genius of a village society. The concept is to travel through time to understand the traditions and defense systems that allowed these communities to survive and prosper in a mountainous and arid environment. It is a journey that celebrates human ingenuity and collective resilience."
    },
    {
        "type": "token",
        "data": "\n\nHere is the proposed timeline:\n\n"
    },
    {
        "type": "timeline_start"
    },
    {
        "type": "token",
        "data": (
            "**Day 1 - Arrival at Agadir Al-Massira Airport**\n"
            "Transfer to your hotel in the city of Agadir. Check in and do a first exploration of the beach and Souk El Had.\n\n"
            "**Day 2 - The Spectacular Granaries**\n"
            "In the morning, depart from Agadir and journey into the Anti-Atlas region to visit the remarkable Inoumar granary. The drive takes about 1.5 hours. Upon arrival, you'll explore this well-preserved fortress of stone and mud brick.\n\n"
            "In the afternoon, continue your journey towards Ait Baha to discover the impressive Agadir Imchgigln. Perched on a rocky peak, this spectacular granary offers a panoramic view over the valley. In the evening, you will check into a hotel or guesthouse in Ait Baha for dinner and the night.\n\n"
            "**Day 3 - The Granaries and the Amazigh Way of Life**\n"
            "After breakfast, the day is dedicated to exploring Agadir Ikounka, an area rich in Amazigh heritage where traditions are reflected in local architecture and crafts. In the afternoon, immerse yourself further in the culture by visiting nearby villages, taking a short hike, and sharing a traditional mint tea with the locals.\n\n"
            "You will return to Agadir in the evening, marking the end of the circuit.\n\n"
            "**Day 4 - Departure**\n"
            "Breakfast at the hotel. Free time before your transfer to the airport."
        )
    },
    {
        "type": "timeline_end"
    },
    {
        "type": "token",
        "data": "\n\nThis unique circuit offers a profound discovery of the Amazigh heritage of the Anti-Atlas.  "
    }
]

SOUTHERN_ROUTES_FLOW = [
    {
        "type": "token",
        "data": "  "
    },
    {
        "type": "circuit_header",
        "data": {
            "title": "The Call of the Tata Valley",
            "id": "southern_routes"
        }
    },
    {
        "type": "token",
        "data": "Discover a secret and preserved side of Morocco with the Tata Valley circuit, a timeless escape far from the beaten path. This is an invitation to explore a land of striking contrasts, from lush, forgotten oases to a vast desert of stone. Wander through ancient fortified villages (ksour) that seem to emerge from the rock and discover millennial rock carvings that tell the stories of past civilizations. This 4x4 adventure is an open door to the heart of Amazigh culture, where authentic encounters and legendary hospitality define the journey. The Tata Valley is not just a destination; it's an experience for travelers seeking to reconnect with nature and immerse themselves in a rich, untouched culture."
    },
    {
        "type": "token",
        "data": "\n\nHere is the proposed timeline:\n\n"
    },
    {
        "type": "timeline_start"
    },
    {
        "type": "token",
        "data": (
            "**Day 1: Approaching Tata**\n"
            "Depart from Agadir or Ouarzazate, driving south through the stunning mountain and rocky desert landscapes of the Anti-Atlas. Arrive in the bustling oasis of Tata, which serves as your base for exploring the region. Settle into your accommodation and take a first stroll through the town.\n\n"
            "**Day 2: The Route of Oases and Rock Carvings**\n"
            "Travel west from Tata along the oasis route. You will stop in traditional villages like Akka and Foum el Hisn. The day is dedicated to discovering the region's hidden treasures, including prehistoric rock carving sites like Oum El Alek, which bear witness to the area's ancient history.\n\n"
            "**Day 3: Fortified Villages and the Jebel Bani**\n"
            "Explore the magnificent fortified villages (ksour) nestled deep within the palm groves. Some are still inhabited, offering a glimpse into a traditional way of life, while others stand as silent, beautiful ruins. In the afternoon, embark on a hike or a 4x4 exploration into the Jebel Bani, a rugged mountain range that marks the border with the Sahara.\n\n"
            "**Day 4: The Spectacular Road to Tafraout**\n"
            "Depart from Akka for a memorable full-day journey to Tafraout (approx. 160 km). This spectacular route crosses the Jbel Bani and winds into the Anti-Atlas mountains. Highlights include the picturesque Igmir Oasis and the Aït Mansour Gorges. Before arriving in Tafraout, you'll encounter the region's famous landmarks: the otherworldly Painted Rocks and the 'Napoleon's Hat' rock formation. Upon arrival, the beauty of the pink granite landscape will welcome you."
        )
    },
    {
        "type": "timeline_end"
    },
    {
        "type": "token",
        "data": (
            "\n\nThis circuit is an adventure for travelers who prefer tranquility and authentic discovery. To ensure the best experience, please consider the following:\n\n"
            "**Practical Information:**\n"
            "* **Best Season:** Spring (March-May) and Autumn (September-November) offer pleasant temperatures. Summer is strongly discouraged due to extreme heat.\n"
            "* **Duration:** A minimum of 4 to 5 days is recommended to fully appreciate the region and its sights without rushing.\n"
            "* **Transport:** A 4x4 vehicle is essential to navigate the unpaved tracks required to access the most interesting sites.\n"
            "* **Difficulty:** This itinerary is for prepared adventurers. The region's isolation and road conditions require careful planning. Hiring a local guide is highly recommended for navigation and cultural insight.\n\n"
        )
    }
]


SPORTY_TREKS_HIGH_ATLAS_FLOW = [
    {
        "type": "token",
        "data": "  "
    },
    {
        "type": "circuit_header",
        "data": {
            "title": "Moroccan High Atlas Sports Trekking",
            "id": "sporty_treks_high_atlas"
        }
    },
    {
        "type": "token",
        "data": "Sports treks in the High Atlas combine significant physical effort with a total immersion in magnificent landscapes and authentic Berber culture. These circuits can include ascending major summits, crossing isolated valleys, and exploring deep gorges. They require good physical condition and adequate preparation, offering an exceptional playground for adventure lovers."
    },
    {
        "type": "token",
        "data": (
            "\n\n  ### Main Trekking Circuits\n\n"
            "The High Atlas offers a variety of circuits tailored to different experience levels.\n\n"
            "**Summit Circuits (Difficult Level)**\n"
            "For experienced hikers in excellent physical condition.\n"
            "* **Ascent of Toubkal (4,167 m / 13,671 ft):** As the highest peak in North Africa, this is a popular and major athletic challenge. The classic route from Imlil takes 2-3 days. The trail is steep, and winter ascents require technical equipment (crampons, ice axe).\n"
            "* **M'Goun Massif (4,071 m / 13,356 ft):** A wilder and more authentic trek than Toubkal. This challenging 5-7 day journey combines the summit ascent with the discovery of the beautiful Aït Bouguemez and Dadès valleys.\n\n"
            "**Gorges and Valleys Circuits (Medium Level)**\n"
            "For those seeking a good physical challenge without the altitude of a 4,000-meter peak.\n"
            "* **The Aït Bouguemez Valley:** Nicknamed \"the happy valley,\" this 3-5 day trek offers a rewarding sporting experience with moderate elevation gain. Discover traditional Berber villages and lush green landscapes.\n"
            "* **The Dadès Gorges:** A unique 2-3 day trek that combines mountain hiking with refreshing water crossings through riverbeds, surrounded by the steep, dramatic cliffs of the gorges."
        )
    },
    {
        "type": "token",
        "data": (
            "### Planning Your Trek: Logistics & Practical Details\n\n"
            "**Feasibility and Difficulty**\n"
            "The feasibility of these treks is excellent with proper planning. The difficulty ranges from medium for valley treks, which require good fitness, to very difficult for high-altitude summits, which demand excellent physical condition and high-mountain experience.\n\n"
            "**Professional Guide**\n"
            "Hiring a professional mountain guide is highly recommended for all treks and is often mandatory for national parks. They ensure your safety, manage logistics, and enrich the journey with their knowledge of the local culture and environment.\n\n"
            "**Best Time to Go**\n"
            "The ideal seasons are **spring (April to June)** and **autumn (September to October)**, offering pleasant temperatures and optimal walking conditions. Winter brings snow and requires specialized skills and gear for high-altitude routes.\n\n"
            "**Accommodation**\n"
            "Depending on the circuit, nights are spent in mountain refuges, local guesthouses (*gîtes d'étape*), or in camps set up by your trekking team.\n\n"
            "**Getting There**\n"
            "**Marrakech-Menara Airport (RAK)** is the most convenient gateway to the High Atlas. From Marrakech, trek starting points like **Imlil** (for Toubkal) are easily accessible via a grand taxi or private transfer, with a journey time of about 1.5 hours."
        )
    }
]






CIRCUIT_MAP = {
    "imperial_cities": IMPERIAL_CITIES_FLOW,
    "thousand_kasbahs": THOUSAND_KASBAHS_FLOW,
    "igoudars": IGOUDAR_CIRCUIT_FLOW,
    "southern_routes": SOUTHERN_ROUTES_FLOW,
    "sporty_treks_high_atlas": SPORTY_TREKS_HIGH_ATLAS_FLOW,
}