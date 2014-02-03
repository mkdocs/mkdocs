# Writing your docs

How to write and layout your markdown source files.

---

## File layout

Lorem ipsum dolor sit amet, meliore deserunt referrentur per ad, mei eros elaboraret no. Soluta sadipscing eum ex. Duo ne nominati definitiones, animal sententiae nam no. Legimus dissentias reformidans an eum, cum cu ferri saepe graece, elitr scriptorem ut has.

Duis audiam vix eu. Vidit dissentiunt nec ea, an dolor incorrupte vix. Has modus gloriatur assueverit ne. Elitr inciderint ea pro. Ad dictas nostrum nec, mei ad alterum fabellas.

    

## Linking documents

Solum nonumy alienum mel ea. Ea brute intellegam vis, antiopam argumentum te eos. Pro ut sumo altera salutatus, modus periculis te his, an vix aeque paulo maiorum. Mea cu dolorum praesent hendrerit.

#### Internal hyperlinks

In cum esse utroque, pri equidem molestie epicurei an, at ludus euismod pertinax mea. Ex nam adipisci repudiare comprehensam. Ex propriae detracto intellegat vel, vel et lorem dicta tincidunt. Mei ne affert mollis voluptatibus. Mel et sonet graecis, ius deserunt eloquentiam no.

    Ex vim diceret [vocibus salutandi](../example.md), qui liber nostrud ad.

Est cu dictas suscipit, ne mel iriure eligendi insolens, cu cum alterum civibus. Vidisse vivendum ne has, pertinax neglegentur no vis. Vel ei referrentur efficiantur, sed facer indoctum similique et. Ad temporibus liberavisse his, nec cu primis electram moderatius. Ex meliore denique has. Eam ea offendit expetenda. Ei error facilis suavitate pri, ex utroque vulputate efficiendi eos.

    Ex vim diceret [vocibus salutandi](../example.md#lorum-ipsum), qui liber nostrud ad.

#### Cross-referencing your documentation

Ex eam quem facilisi deserunt. Veri audiam audire id his, quo at aperiri moderatius. In admodum partiendo est, ei rebum minimum eam, singulis accusata delicatissimi eos ut. Imperdiet vulputate assueverit eos an, elit recusabo et usu. Eam ad euismod accusata vituperata. Oratio vocent nominavi ei eum.

    At mel verear persius torquatos, his dolores [Sensibus](ref:) id, alia urbanitas in usu.

Eam ad euismod accusata vituperata. Oratio vocent nominavi ei eum.

    Ne his mucius oporteat, [mea ut eros delicatissimi](ref:delicatissimi), iudico nonumes moderatius an mel.

## Images and media

Ex vim diceret vocibus salutandi, qui liber nostrud ad. An eius postea nam, cu labore argumentum cum.

    At mel verear persius torquatos, his dolores.
    
    [!Sensibus](../img/sensibus.png)
    
    Alia urbanitas in usu.

Fuisset nostrum eos ut.

    docs/index.md
    docs/api-guide/sensibus.md
    docs/api-guide/dicant.md
    docs/img/sensibus.png

## Markdown extensions

Quas malorum vituperatoribus mei et, ei augue dicant pri. Etiam denique temporibus ei vis, sea an dicant malorum petentium.

#### Page metadata

Unum errem propriae vis cu, et deseruisse interpretaris eam. Illum graecis per an, ludus laoreet repudiare nec an, molestie recteque et eam. Purto duis rationibus id eum, pro et amet appetere referrentur, minim impedit ad ius. Et nostrud perfecto sapientem vix, et dicit impedit consequat vim. Vis liber blandit no.

At mel verear persius torquatos, his dolores sensibus id, alia urbanitas in usu. Te pri cibo blandit. Debet dolore periculis ei pro, eu vis vidit ignota, vim natum dicta cu. Et appareat delicata vix, mei at solum lorem quodsi, verterem electram sit eu. Eius malis cum an, pro malorum euripidis ad, oblique appetere est cu. Eos ei fugit deterruisset. Vix ei aliquip dolorem, usu te euripidis reformidans, volumus pertinacia ea eam.

    page_title: Lorum
	page_description: "lorum ipsum dolor"
	source_files: example.js, lorum.js
	
	# Lorum Ipsum
	
	Unum errem propriae vis cu, et deseruisse interpretaris eam. Illum graecis per an, ludus laoreet repudiare nec an, molestie recteque et eam.

#### Tables

Unum errem propriae vis cu, et deseruisse interpretaris eam. Illum graecis per an, ludus laoreet repudiare nec an, molestie recteque et eam. Purto duis rationibus id eum, pro et amet appetere referrentur, minim impedit ad ius. Et nostrud perfecto sapientem vix, et dicit impedit consequat vim. Vis liber blandit no.

    First Header  | Second Header
    ------------- | -------------
    Content Cell  | Content Cell
    Content Cell  | Content Cell

Ut qualisque suscipiantur nam, probo solum incorrupte sed no.

#### Code blocks

Unum errem propriae vis cu, et deseruisse interpretaris eam. Illum graecis per an, ludus laoreet repudiare nec an, molestie recteque et eam. Purto duis rationibus id eum, pro et amet appetere referrentur, minim impedit ad ius. Et nostrud perfecto sapientem vix, et dicit impedit consequat vim. Vis liber blandit no.

    ```python
    # moar python code
    def init():
        yield init
    ```

#### Admonitions

Ad est nibh suscipiantur. Quaeque deleniti delectus an has, tempor accusamus eu vix. Et democritum expetendis nam, putent fuisset duo ea, elaboraret efficiendi no vis.

    !!! danger "Don't try this at home"
        May cause grevious bodily harm 
