import json
import re


CIRCUIT_INTRO_MESSAGE = """
Hello! Welcome to your Moroccan adventure. I can help you find the perfect journey tailored to your interests. Below are our curated circuits, each offering a unique experience.

### Imperial Cities Circuits
Step back in time and walk in the footsteps of sultans. This circuit connects the four historic capitals of Morocco: Fez, Marrakesh, Meknes, and Rabat. Immerse yourself in the vibrant energy of ancient medinas, marvel at the intricate architecture of palaces and mosques, and get lost in bustling souks filled with spices, crafts, and timeless culture.

### The Thousand Kasbahs Circuits
Journey along the legendary "Route of a Thousand Kasbahs." This path winds through dramatic desert landscapes, lush oases, and breathtaking river gorges. You'll discover iconic, centuries-old mud-brick fortresses (Kasbahs) that rise majestically from the earth, each telling a story of ancient caravans and powerful dynasties. It's the perfect choice for lovers of history and epic scenery.

### The Igoudars Circuits
Venture off the beaten path to uncover one of Morocco's best-kept secrets. The *Igoudars* are fascinating and ancient fortified granaries, unique to the Amazigh culture of the Anti-Atlas mountains. This circuit is for the curious traveler looking to explore authentic heritage, stunning remote landscapes, and a piece of living history that few get to see.

### Southern Routes Circuit
Embark on the ultimate Saharan adventure. This circuit takes you deep into the heart of southern Morocco, where the world opens up to vast desert landscapes and serene oases. Experience an unforgettable camel trek across majestic sand dunes, spend a night in a desert camp under a blanket of brilliant stars, and witness the raw, soul-stirring beauty of the Sahara.

### Sporty Treks in the High Atlas
Answer the call of the mountains! This circuit is designed for the active and adventurous traveler, offering challenging and rewarding treks through the stunning High Atlas range. You'll hike past remote Berber villages, cross dramatic mountain passes with breathtaking views, and experience the majestic nature of North Africa's highest peaks up close.

---

**Which journey are you ready to begin?** Just let me know the name of the circuit!
"""

def generate_id(title):
    """
    Converts a circuit title into a snake_case ID.
    Example: "The Thousand Kasbahs Circuits" -> "thousand_kasbahs"
    """
    s = title.lower().strip()
    # Remove "the " only if it's at the start
    if s.startswith("the "):
        s = s[4:]
    # Remove circuit/s suffix
    if s.endswith(" circuits"):
        s = s[:-9]
    elif s.endswith(" circuit"):
        s = s[:-8]
    # Replace remaining spaces and special prepositions with underscores
    s = s.replace(' in the ', '_')
    s = s.replace(' ', '_')
    return s

def transform_message(message):
    """
    Transforms the full message string into the target list structure.
    """
    CHUNK_SIZE = 10
    output_flow = []

    # Helper to add text in chunks to the flow
    def add_text_in_chunks(text):
        # Use regex to split by spaces and newlines to better handle formatting
        words = re.findall(r'\S+|\n+', text)
        if not words:
            return

        current_chunk = ""
        word_count = 0
        for word in words:
            if word_count < CHUNK_SIZE:
                current_chunk += word + " "
                if '\n' not in word: # Don't count newlines as words
                    word_count += 1
            else:
                output_flow.append({"type": "processed_token", "data": current_chunk.strip() + " "})
                current_chunk = word + " "
                word_count = 1 if '\n' not in word else 0
        
        # Add the last remaining chunk
        if current_chunk:
             output_flow.append({"type": "processed_token", "data": current_chunk.strip()})


    # 1. Split the message to isolate the main content from the footer
    if '\n\n---' in message:
        main_content, _ = message.split('\n\n---', 1)
    else:
        main_content = message

    # 2. Split the main content into the intro and circuit sections
    # The (?=...) is a lookahead that keeps the delimiter in the next split item
    parts = re.split(r'(?=\n### )', main_content.strip())
    
    # 3. Process the Intro
    intro_text = parts[0].strip()
    add_text_in_chunks(intro_text)

    # 4. Process each Circuit
    for section in parts[1:]:
        section = section.strip()
        if not section:
            continue
            
        # Add an empty token to separate sections visually if needed
        output_flow.append({"type": "processed_token", "data": "\n\n"})
        
        # Add the full circuit text block in chunks
        add_text_in_chunks(section)

        # Extract the title line to create the link
        title = section.split('\n')[0].replace('### ', '').strip()
        
        link_data = {
            "type": "circuit_link",
            "data": {
                "title": title.replace('Circuits', 'Circuit'),
                "id": generate_id(title)
            }
        }
        output_flow.append(link_data)

    # 5. Add the final separator
    output_flow.append({"type": "processed_token", "data": "\n\n---"})

    return output_flow

# --- Main execution ---
if __name__ == "__main__":
    circuit_flow_data = transform_message(CIRCUIT_INTRO_MESSAGE)
    
    # Print the resulting structure in a formatted JSON string
    print("# In your Python service file, replace the old constant with this:\n")
    print("CIRCUIT_FLOW = " + json.dumps(circuit_flow_data, indent=4))