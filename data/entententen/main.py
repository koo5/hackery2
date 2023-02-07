# first data form, raw lines coming in from dictation, a google doc dump, or similar

raw_dictation_text = [
    # as may come from, for example, dictating with google keyboard into a text document

    "BME280's are i dont know where",
    "ultrasonic sensor, 2 pieces, are in green box",
    "W600_PICO, 4 items, are in MCU box",
    "W600_PICO has note 'https://www.wemos.cc/en/latest/w600/w600_pico.html'",
    "green box is in upstairs room",
    "Kleště Jsou v garáži",


]


english grammar:
item_is_in_unknown_location = item, " is i don't know where"
item_is_in_unknown_location = item, " are i don't know where"
item_is_in_location = item, " is in ", container
item_with_count_is_in_location = item, ", ", number, " items, are in ", container
item_has_note = item, " has note ", note
item_no_longer_exists = item, " no longer exists"





markedup_event_text_log = [

    """<item_location_event>
        <item>BME280's</> are <container>i don't know where</>
    </>""",

    """<item_location_event>
        <item>ultrasonic sensor</>, <count>2 pieces</>, are in <container>green box</>,
    </>""",

    """<item_location_event>
       <item>Thermocouple sensor + module</> is in <container>green box</>
    </>""",

    """<item_destruction_event>
        <item>bag of cables</> no longer exists
    </>""",

]

# the item_destruction_event phrase may be useful for example where some aggregate item is transformed into some individual items, which can then be introduced by item_location_event



event_log = [
    # events with unique or specific identifications of items and containers
    #  this is concievably gonna bring up some interesting cases, like when an utterance ("pliers") needs to be disambiguated based on recent history of events, or where an event is gonna reference an item by basically an existential, based on some properties...shrug

]




inventory_by_container = {
    # key is the immediate known container that the items are in
    #--------
    # to have the data in this form implies functioning unique identification of containers
    #  i'm gonna start by using descriptive name strings, but eventually these probably would become opaque uris
    #------

    "garage":
        [
            # these things are only known to be *somewhere* in garage

        ]
}




def nested_containers_markdown_with_full_item_details__to__inventory_by_container(nested_containers_markdown_with_full_item_details):
...






nested_containers_markdown_with_full_item_details = """
* garage
  * blue box
    * lightbulbs

"""
""" ^ note:
this form ignores the ambiguity between knowing that an item is "contained" directly by "garage", and where an intermediate container is unknown. We could also have this form:
* garage
  * <unknown>
    * lightbulbs

""""






def items__to__item_stock_up_log():




