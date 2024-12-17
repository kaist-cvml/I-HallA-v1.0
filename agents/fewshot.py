fewshot_captions = ["An ammonia molecule (NH3)",
            "Tutankhamun's golden funerary mask",
            "Golden Gate Bridge in winter",
            "The Mount Rushmore National Memorial"]

fewshot_responses = ["Weird", "Normal", "Weird", "Normal"]

fewshot_reasonings = ["""- Response: Weird
- Reasoning: The image is labeled as an ammonia molecule (NH3), but the structure depicted does not correspond to the molecular structure of ammonia.
  - **Visual Evidence**: The image shows a complex molecular structure with multiple nitrogen (N) and hydrogen (H) atoms arranged in a tetrahedral geometry. In reality, an ammonia molecule consists of one nitrogen atom bonded to three hydrogen atoms in a trigonal pyramidal shape, not the complex structure shown in the image.
  - **Contextual Evidence**: The labeling in the image includes multiple NH3 groups and other hydrogen labels (H3 and H), which do not make sense for a simple ammonia molecule. This suggests a misunderstanding or incorrect representation of the actual molecular structure of ammonia.""",
  """- Response: Normal
- Reasoning: The image shows the iconic golden funerary mask of Tutankhamun, which matches historical artifacts and widely recognized depictions of the mask.
  - **Visual Evidence**: The image presents a golden mask with blue and gold stripes, a nemes headdress, a false beard, and a uraeus cobra on the forehead. These features are consistent with the known characteristics of Tutankhamun's funerary mask, which is one of the most famous artifacts from ancient Egypt.
  - **Contextual Evidence**: Tutankhamun's funerary mask is an important historical artifact discovered in the pharaoh's tomb in 1922 by Howard Carter. The depiction in the image aligns with the historical and archaeological records of the mask, confirming its authenticity and accuracy.""",
  """- Response: Weird
- Reasoning: The image shows the Golden Gate Bridge in a snowy winter setting, which is highly unusual for its actual location.
  - **Visual Evidence**: The image depicts the Golden Gate Bridge surrounded by snow-covered trees and landscapes, with a thick layer of snow on the bridge itself. This is visually striking but inaccurate.
  - **Contextual Evidence**: The Golden Gate Bridge is located in San Francisco, California, a region known for its mild Mediterranean climate. San Francisco rarely experiences snow, especially in the amounts shown in the image. While the bridge can occasionally see light frost, significant snowfall and a fully snowy landscape are not characteristic of the area's typical weather patterns.""",
  """- Response: Normal
- Reasoning: The image depicts the Mount Rushmore National Memorial accurately, showing the carved faces of four U.S. presidents in the Black Hills region of South Dakota.
  - **Visual Evidence**: The image shows the iconic faces of George Washington, Thomas Jefferson, Theodore Roosevelt, and Abraham Lincoln carved into the granite face of Mount Rushmore. The details, proportions, and setting of the sculpture match the real Mount Rushmore.
  - **Contextual Evidence**: Mount Rushmore is a well-known historical landmark in the United States, and the depiction in the image aligns with the actual appearance of the memorial. The context provided by the caption matches the visual representation, confirming that this is a factual and accurate portrayal of the site."""]
