#!/usr/local/bin/python3
# <bitbar.title>Moode audio player volume controller</bitbar.title>
# <bitbar.version>v2.0</bitbar.version>
# <bitbar.author>Piotr Gołąbek</bitbar.author>
# <bitbar.author.github>piotr277</bitbar.author.github>
# <bitbar.desc>This plugin allows volume controlling of local running Moode audio player. For more information about Moode check this: http://moodeaudio.org/</bitbar.desc>
# <bitbar.image>https://github.com/piotr277/moode-vol-control/raw/master/moode-vol-control.png</bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>
# <bitbar.abouturl>https://github.com/piotr277/moode-vol-control</bitbar.abouturl>
import json
import requests
import sys
import os
import io
import base64
from PIL import Image, ImageOps

# leave as it is if your moode and network supports mDNS or enter direct ip address
moodeUrl = "http://moode.local"
# set full path of this script
scriptFilepath = __file__
# value for volume incrementation / decrementation
delta = 3
# ui mode: light or dark
icon_mode = 'light'

icon_online = "iVBORw0KGgoAAAANSUhEUgAAACQAAAAkCAQAAABLCVATAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAAFiUAABYlAUlSJPAAAAAHdElNRQfjCQcKKCCnZ5LwAAAEd0lEQVRIx5VWXWwUVRT+zp2Zndlu92922253t9uytaT/Lf2zEhVsIgrG1DbRRIsaqzUkihFJ0IgIVqMS39AHIxGUhBhMiMKLCSbyoI3Ellq0KRUVRcA20kJbW9ou3T0+7A7702mp9z7szbnnfPPde8757hKWGCwCjbPV82vmg1khwsxf2kV5IHvwdK9vwdyfzIwFeZGdY1tjEWlcPSUP2K8AUx5umG2KeoTF+6HSfWkEtxqlAFzfgfXfGiohb0v7zC5S5Poy/SzY1cdUsjRIHYDCl4gdp/KLAaBrkcfTAIDAKte3xIEdQKUZTDUAx36FA08CVcuyrgcQfExhxyfxE6SNWgCez+WJjTpWOB52yePuY0B55obzoDwBQECAEjO5okRSjFXiVx5zHAZeToKUIPiKwu2utMDMiRSIxHzGrrCvO4XNpAwueBRYxGJZGBBQ1AZ+05Y81o/ukynU43AisRIm4XnJCnQftw9zfBkIgkOFTViGUQqffGE9rfzLgggErEUoQBwoBADkHXH3pFR6GsCd+XXZKeAAger8gtVvkpw8J/QvATxnF1wVWAyjCMDxPrG8x+DjRZsKEAHO18Che41v1+QKbnchp4WmQ/LWVCBBBKryqX1gMN5IplvrU7+PQymj8qVcEQ9aLdGUdwPcO7Tf+ebJXpShPm4Bcu4mBmcCubaA/R0A4OiiaCDLiLINu3fD+UX+AcMQLo6HW6fBSAMqkHMJBGQNUaRRAflWgws6jLjgB7bjIlbq6DUMFz+Nc5u1pVd9jX30SnQPGFC3szSsA6PnCJObjH1PP8rEvKpcMAw3JPO+OjMlD1x7vVMSFPkTIqICgBqLhI398/1zmmBEoyvo0WjyHpkyFVGKkiy0BSm0rFwyUOm80aC/fSAaY0sRYuocwJgTyh+Gy6oq5bpYGJ6qNQy+vWQqxoNTud7ILhAwv5eipVcBXwnD9ZXh8ndZ7Bz0t+xDCaUG0KDA0uTIKdAuwCz9XWD/E0b6gzfT7x5wvwd9I01USIsqG7Z9tAhI61d/AEgAlhH5si9RkLUSruqtuCtHcLXTpNOQ+5CYSQAJCJAsWjQWRIDjVXDwfuNK6+2C1/gBuHryD5u2LNXZLGPubWmqICDqfYItJ5O58X/k/jne/SXE5d4HTfufEc4Ad0vWM8rMIYkIAtiMWp04VAEAeEFYx737zBgtpZZFvqSO576rTXaK7XESG0KCSxvT5B0ZD4AweQ4IqKoR3Jz6JrkPaZMAZapiUnpNgIgAbcz5WQrMAwBsPdovca1JEVYsgkyDsZ619QPrU8s3jKcU+3nrMP7HsA7ZRtot4UxzgB5RbL3aWGUV8OyyAM8DqC61jmT/1KaaOhQDcB6ROKe72bkc0DpH3k7BjqNAeCmXFgDNldo0sf+dO6zrROb+erHW6t9NbLne2ADcc6s/WvdJv9ZeOzYRoHG9z3rU17dpBvy17XLjdOvE7VGv6x9Pa3HfiYUVXOIWAEDFbXpH9n77YNZcFmexbd4+lP2xvrm8BAA6TaL+A1qkORgvHNnaAAAAAElFTkSuQmCC"
icon_offline = "iVBORw0KGgoAAAANSUhEUgAAACQAAAAkCAQAAABLCVATAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAAFiUAABYlAUlSJPAAAAAHdElNRQfjCQcRHxuWGJdxAAAEQElEQVRIx5WWW2xUVRSG/7XPZc50Ovcpvcx0Cq0jvcyU3q1EU+ChCKQ2baIJSGLES0wQEzVBEmJI6oO++GJ8UAlImqDBpFEuiUl5MEZqCC0VaYVatIkUbMS2tE2hFzuzfJg5nTMzp2Xc+2H2OWuvb6+99l7/GcIajYW/caF6qXYpkBMkPLitjcvXcoev9hesmM8ns5fF+ctHJw/FlqUpy2X5mv0fYM7LDQtNUa9QfZ8qXXcm8KhWDsB1Cez5vSEM+a2UZd4jRa6v8NwEuwaYQmtD6gCUvE3suFxYBgCvZsx4GQDg3+T6kdh/GAibYaoBOI4r7H8RiKwbdT2AwD6FHafiO0hpNQC8X8szuzzIsj3nkqfcZ4HKdIPzC3kGgIAAJXpyRIlD0UeJX3nScRp4NwkJIXBE4U5XimN6hwGR6K/YFS7oMkQzK4OL9wIZURCICJCFGQYEbOwAv29Lbutn9/eG0OM4kRjB0WOG0G+g+5x9hONDfwAcLGmCWURX4OgWbBJP/AlbEfQT+0sAAPln3H2Gm54y3fklWOKMNBsPAN5ez7cADtoFR/yZGBKA/QQ4AcJaGGDLBsGdLuTtoPmgfMgIimcIts/AqyACaaLKxRAEAlq8ySw9LtGcrxXuw9ofiWRBLVHr1Dq1Vq1T6nJPxTE6SFCrog5brjCAQJPE+fuAzoSfbcR9DM5vCk+uZuik7mzsiYigjIHB2mg4LBgMLnlGdwt8YjsnYuWO/qQIrVMTVHCQACyGfh2KAVDvxn7QTd5BVIgli/JndtU1/p3vWUqspvZfDY4v6paxwUVNMKLRrDgESNNCf5iOxJImKUqy0FakYFYgLm24d0lfc2mnNlQs66ZNEeWhWBmZq8kOdPt8DIA6WbqbACyGea9u+qsiNipbr9/XTxHWX3BBd1tujVqMHEGbQ6MjtNBaeeHfgra/z3uP3OluRPyclttyLsKzi2aqJABwpgTwlF0dS72QkthY1GERBAFUbE5eyBoJ0552PJ0nuNqZWSJ26pHVW6sgkaIJKUVSbxdcWwTA1Vd42qxkJfpIWMYMoHj5iHRQ0efuoXj1h4grfW2m9b9H2H4SnPJWGKDYjxoPcbAKAPCmsE75PjYREV1KetewEABs+FCbPSDeiQfRGhRc3pgi76tKIJHhk5AuxIhsEdxs/Ca5u7VZgDI1MHU7Il3NtUnnVwbMHgC2Pu03gChFxGCqi6sY603bILDNeGtK8ZJiH7OO4H806w3bRKdamv7aT88rtn5tMhwBXlsX8AaA6nLrRO71DovphDIAzjMS53U1O9cDtTjyjwp29ACla03ZAaA5rM0TF33wpLVFpNu3ia3WomPE6sPGBmD7o/5o7ZRu1dw/O+OnKc+AtadgYPcD8EXb3cb59pknoj7XPW972UDvShZJfB0AUPWY54Xc4/bhnMUczmHbkv1G7gnP/soQABww8foPneIw6Uqt8W4AAAAASUVORK5CYII="
icon_v_up = "iVBORw0KGgoAAAANSUhEUgAAACQAAAAkCAQAAABLCVATAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAAFiUAABYlAUlSJPAAAAAHdElNRQfjCQcRHyuwwafdAAAEJUlEQVRIx5WWbWyTVRSAn3Pft13fdu3abmOwjk42ZsbYxnAbbBgDQjICSiZLFFESI37ERDFREzUhxmT+0D/8ITEholFJwGBCAkYSw2aIH0OSTSRI2EDFKMoibKwlsLml3fVHP/b2Yx/ek7S355z7vOfee855K8wytAq1TjROrp6scIeFu3+6rpnnCy/+2L84lt9f8imXlk3tHdkzPWWMFpw1z3tvwu1i3TKxJl6snCUHHN1/DTPfqAX836ODv7bUY76S8Zi3xGE2rwgOov0DWmpmh9wHVL4q2nd2STXAczkezwAQWub/TnTodajPh2kEfAcdOvQUNMwZdTNQ8YRD+z5J7CBjNAHFn5uRLUEWOB71m6OBE1CXbSj62IwACoUkZWYmyUtJzZLf5ojvMLwxA6mh4k2H7vJnLMwWbIikPOt16MXdtmiiJnrpTsiJQhBDwK3yYRC4Zzv6Hc/Mtn4KnLaFnsCp5IzSffkQqQwMfOEd0olpqAIdrlxDvog6lPuM80qeeBK/WEc4JDpUCUDZ0UCfLdPTogQ8A+iCwZxjtl8AxaeCx4EXvUo3hHIxhgL3aXQSBAJmOtOVzBTXqkVKd/kp3Sh3wuYeO0ghosA6iU6DkhFUtVhHrCPlm1JbA7jXkNslHWaspeCfP2IJXVENyRvQEts3viG3sKcqJnaC9S1fz+iuxD3X4+3mdHvgm5Rn9BBr83WU+bI80DvWbE7X+vYPz79Es4kypm+1Aoy3EkW4SU/yuM+NbcZ5tX5r2v2HxKlkSvKwz+RYBlLLvE3GNaWJxxdUpXp2jREX03TFjPBCOP4P6dXTrIjugMKTRr8I1yJJ27KGoXEzNnS7aQEciXyKRlc8Et0Bzi9vHbDf5fUV01dM68JYV0rh+IrfUmHHHtdGRkfXWakgM1ub2ubuIbhFIisNACsjhOWV5khuQlbf7+61essfTlZloika3Ap28kCp0o1FuSXikbageSMNUgjKkY7HsNVas1fp1eWAv2/J4VwQYki7ZUZtoET5qOyiLf8g8HOi+mtE15VsIx+szlnwu/NyhlbZoOyiKSg6vBKAl5U1WrI/F5J6aun7s1gEYNF7ruhu9VoiiI6w0rWtGe093QkciVar8rwOBBpWKd1mfycFDrmiILk9MHM7GSARcI0UfWbDPAR4+lyXQSSdLZL1mSUiYA16zsEGe9ZU8bTDe9Ua4n8M65JnuMtZla0OyWMOT79rpL4Bnp8T8BLQWGsNF17YXpDXoRooOmro0u62orlA631le5X2HYOq2Vw2Am31rjuiy99tt9arbPsGtc4qf1u0c7y1BR6c74/WZuOXprETkZCMBgesY4sHtt5F93j+br3TGVkbL/HfKO6sHjgVW8AhvgDAyuXBJwsPei+6/3Vrt/ZMei8VfhTcVVcDsDvPqv8APTQqJw/LBgYAAAAASUVORK5CYII="
icon_v_down = "iVBORw0KGgoAAAANSUhEUgAAACQAAAAkCAQAAABLCVATAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAAFiUAABYlAUlSJPAAAAAHdElNRQfjCQcRIAKqrRWNAAAD8UlEQVRIx5WWf2hbVRTHv/e++5K8vPx6L9na9XXp1prRtUkXbbO1/Wd1f3RsY5QVHP4YiPMHgk5QQYUhQv1D/3D/DARxiDoYMmHiBEG2wRCtDhrnmGPtqm5odVGXmqR2rS1Jrn+8l+S95CWN5/LIfeee+7nnnnvPeSGoI5xqieW+lXtX2t1hgru/uubYFc+176Za8/b2xE65sWX1aPpIcVWYd15iV7x3gIUgH1jeXghSR+gdceK3FNaSbgCBr8HVnwaiYM9blnmViKx/qzoNHkhyEqkPuQ9AxwuE+y5t6AKAJ2ssHgcAaJsDXxGuvQRE7TB9AHwnRK49CsQaet0PoP1hkfs+0HdgkTiA4Mcsu0dFk/JAgM0rZ4Ge6gH/+ywLgIKCGK3SI8ahlHrGL0v7TgEvVyARtL8i8vGAZWJ1gwlhtCe8Im+dMHmTY+AbHwJqvCAgAgGc1A4DAmw6AP66XNnW98pFk+s6jho9KMfsEKUbqHzmneF6V2sHD3dsh51Ho9T9jTBr44/+hmGENcK1DgBAy2ll0nTTy40SQE6CC9M1YTYfAILn1E8BPOOlPKbVYgQKuC+CGyDUwwDb1lM+HsC6XWQxzI6YQRSEUED6HLwMqneSALYIZCE0yvIDzj9/yes6fwTGCXCSP7Y00iixKzJbkG8XhlhxSPmyZJk7iR12FWWtW65cyPSzYrfveGrtKbz14EqoMk7ACf7IfGKE+3JmNxw3o3vL5t/qUbE2PdjSdM3IVGmaNy7MUY5CoaksLdbfslAgjLnyQrgZjvwh06pUt/4xOptjM0ssP7MQb4JD0m/Vj+DtrcVZJl3NjJcU4hf4ueR2/kEuWA6e11T7smZ1v/s81D0k2ysAgGSxi4RZus6F1FOalpaJC/hbHaO9SeIXPACwbDFPzSW2sDuWr03p4QC4KdRuqnRMAQhMbjhVm2sgAhmWWM7wiJa9odUp0vau8oOe/RHCe0L7YQeLOpy3hBsWLTVBcQhxlfBwLwDgOSrNh47XQkqrBt5ulLTr33TlDtMXdSdGw5R3JyzlvVwJRAKItFwvq0CxbZQPmr9JyklXDiC1NdC6HQuIEMCV9n9kwuwDIE+6bgCEWIoYbOtiGSNNy5eBEfOt6cRjovemNIP/IdJ1OTXu6KxWa+SgKE+50tEY8FRDwLMA+rqllOfqAaetQRcA/2mBr5sY9DcC7fS1HKXcdwborGeyC8Bg1LVIeNsbQ9JOWj0+QoelttcIdywlBoD71/qjtVv4MZ45m9XIvJqUzrQm994FPy//nlgcy+4ohAJ/Bce6kufyTQTxaQBA7z3qI54T3mvuf93czeUV73XPe+qhnggAHLaZ9R9RaRjH7Pf19QAAAABJRU5ErkJggg=="
icon_pause = "iVBORw0KGgoAAAANSUhEUgAAACQAAAAkCAQAAABLCVATAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAAFiUAABYlAUlSJPAAAAAHdElNRQfjCQcRIQBduEXgAAADc0lEQVRIx51VXUxTZxh+vq/n0J/Tv9NWQU5tBwxSftcNiuCNPxcaXQyRRLIxEnSbZsuEZFxsJsYsYRfbjRe7WUyI0ZgYo4kXeqne+AMxUtEYos6pCWzQsbahMBCpbd9dEOxpOW0pz7n58r7Ped6f7/vejyEHiCuBpablj5fdJg/D4qThL+GxefzhaFlCm8+0jFtL4ycjfam4Lqq/Lzy2hIF5J7UstSadvMR1Rhz8O4RC8AGw3wM5XrY0QPg+I8wpJgrNtY5nIHuQWHVukU8AeAcYWe9vqQKAo2sYXwEAlAr7XUbKD0CDlkwTAOuQSEov0Jg362YA7m6RrOdXKsiAH4DzihDb58A6ccguROVrQF22w3ZOiKFICBHrReDHtKEa7hMiddqBgXWL9AH42iJS2aDKOCeAtn6ODeCDg6CfpffnyPaIx2Z3pd0uW6R8dV36aiYOQETV6plzTUfm0lz5eqJm3scAQHGDPN5WVRxXL2j121wNBgZv2uLqTTO3w6MwUrwABxKn5ZHJiQfqjFOqJa3cGG3vCCanHDeXfgP4d5Zwl7srdxdYwT65e2IdnXZ+JUCLczN9+bmZapTpXIrSf3dahUSLfmYiwYrZqizyi6Q0nWznqXb5dj4ZWkd18q14M0/5rKMFwlN2MdlwjqGWL+vFiSLq0MTrsbcGTkgmterJ0VlN6JJM4IaEzlMgDZY7zAoqGsU3PPF83l+wRwUwXZt6wY1P1LdMY9doTQ5r2hY/YBrnGF4or9flTp5xADxfKL9u1sPu8fogs+nMRWWU3WoTl72j/G7YOhL+fQN7/h6h07bxR9Mc0B/+p7vOdUDtU5XCGADKkFate+B3hI5aPgMY0M+HwtLFSL/2YHO+jL7LN9g2/zr/bbcsr4yWPR5OvsBGRm3jR5za1G+SfMEwB1QUJVIDwBCxXVKZPgUgDRv+KEbKB8D4TBoDdqrNlTgiWl4bnxeTkfGpFOosqcw2K6xLlEYNkYZG4FhegeMAmnzGkPnJQb0moQqA7bKONg222fIJ7bCWnuRkvQpU5qLsBtDWYFhgVP5Lu3HHmouxk283lv/EqORNoAXYVegM79X96Z+9FlNY1BE0Xi0L7l8E3ZSmAgsdsW1Jl/1fZ0dV8EZiHU38BgBQ/6HjC/OQZdz01kQmkpYtT81nHT111QDwpcZf/wNEmQ71Z0gygwAAAABJRU5ErkJggg=="
icon_play = "iVBORw0KGgoAAAANSUhEUgAAACQAAAAkCAQAAABLCVATAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAAFiUAABYlAUlSJPAAAAAHdElNRQfjCQcRICx2exhCAAADkElEQVRIx5WWT2wUdRTHv+/NTHe2y87+6ZaWbrtAQNLSbmntrrRGpHLAYEIammgiF8SYeDCa6MGYEGNSD3pVL0YPGBOimJCIR2zS+KcR0lIJEiigJFJsQ2ll25TSbnb2edh/s7Ozu+Obw2x+vzef9978vu/tEKqYcDT5uHezf7O9MUZ4dFefU69suXZ5qjXj7E9Oix0t6VNLb2bTyrLnonrF/wBYbZLE46fMJm6IfK6N3VuAGwv+Cgn/meiB+nZZmPdJUwe6wjcgwWmhOpDt75AYF7ftquUT3Rn8hST6bg0X40tNoifcZN1+XBPjqyqbTd+pqSNhuLQXg+py6LzDRuC0mgLAYNBe9Rk/gE9Alit3NLlf+bu6ZJyxp/qeJqPBwkMdnFMAxjXFAioh8tdrfk1axyyYFRXS8TIAAoNAKuVBgjmDq2FAwI5jkA99pbJ+D01YUi8UIhAIFj1GBYBKCgz94J8tHGc7JLY9D+IipgASrHHcFqaQHYBYlCSae7rlbGjSovRKkEDogGNxudO+EP4ewBt+lni0DOMAgignnTHAvq0so0E0H6K1mFofBKHTtuPP++1RaDVymDMJz/27GTcSlFdovBjCYrfMxnlziLNDoZ/cqlkO8SVVZbLPjNB4eoCzncYUXFs2Yc6zXtFcM+jiTY/2d/0JVdqVSGbOvnhnZkNngWmW51+7Onqg7rAvKiaprGeUmHsQzXhi5npJjjnbGdfWOTO72leGqVEa/yzJjU2RvDSKNt+VvcXeqw+fc4n5Njvs/C7TRxuvIXyEUt2KC2W/XtxnUG5u5dz6FPwbHsGBZpbeQD0QPQvkARVNMuBn6W8DEJzcdqYWiDaUJy3ZsB3U9kXoj1z3P0GyN1LW/1bQomqUtWsJxQDQFyaJdQMA3mLvcuTTKoPtXqNSMYvKvLZ+rK+8yvnQh2MsnUmHeTTBXDbw2A6K72MZ7LS23df6CkCWSP1EnxWLZScQEaAvBb6xqcQ3qd8EiADAQza9OJRFBHhv+GYq5HZS89/xzuJ/mPe6b2G0ofIfnV7SfFP6Uk/cDaS307uw5eoxT1WHwFlFmscGA7UgB42WUyzGuTqxBnv0NZK2j4a8B9m+N8xPe9s+IGlYTyZcfGg9r9zue3g+FaXl8LT3XOv0C48gP/r+Sa6NpPabkeBi08iu6QsZV19sANC9e2F/epiGzN3wAJTmv+S3honWS9dvO/v/B+RBICmEFVsIAAAAAElFTkSuQmCC"

def getIcon(icon):
    if icon_mode == 'dark':
        decoded = base64.decodebytes(str.encode(icon))
        image = Image.open(io.BytesIO(decoded))
        # split LA channels
        l,a = image.split()
        inverted = ImageOps.invert(l)
        # create new
        result_image = Image.merge('LA', (inverted,a))
        buffer = io.BytesIO()
        result_image.save(buffer, format='png')
        result_image.save('/tmp/inverted.png', format='png')
        encoded = base64.encodebytes(buffer.getvalue())
        return encoded.decode().replace("\n", "").strip()
    else:
        return icon

def getVolume():
    r = requests.get(moodeUrl + "/command/moode.php?cmd=readcfgsystem")
    result = r.json()
    return result['volknob']


def setVolume(volume):
    requests.post(
        moodeUrl + "/command/moode.php?cmd=updvolume", data={'volknob': volume})


def getState():
    r = requests.get(moodeUrl + "/engine-mpd.php?state=undefined")
    result = r.json()
    return result


def play():
    r = requests.get(moodeUrl + "/command/?cmd=play")
    if r.status_code == 200:
        return True
    else:
        return False
def stop():
    r = requests.get(moodeUrl + "/command/?cmd=stop")
    if r.status_code == 200:
        return True
    else:
        return False


# get cli arguments
if len(sys.argv) > 1:
    cmd = sys.argv[1]
    if cmd == "up":
        try:
            v = min(int(getVolume())+delta, 100)
            setVolume(v)
        except:
            pass
    elif cmd == "down":
        try:
            v = max(int(getVolume())-delta, 0)
            setVolume(v)
        except:
            pass
    elif cmd == "play":
        try:
            play()
        except:
            pass
    elif cmd == "stop":
        try:
            stop()
        except:
            pass

try:
    volume = int(getVolume())
    state = getState()
except:
    volume = -1


if volume != -1:
    print(str(volume) + " | templateImage=" + getIcon(icon_online))
    print("---")
    print("Volume up | color=orange terminal=false refresh=true bash=\"" +
          scriptFilepath + "\" param1=up templateImage=" + getIcon(icon_v_up))
    print("Volume down | color=blue terminal=false refresh=true bash=\"" +
          scriptFilepath + "\" param1=down templateImage=" + getIcon(icon_v_down))
    print("---")
    if state['state'] == "play":
        print("" + state['title'] + " | terminal=false refresh=true bash=\"" +
          scriptFilepath + "\" param1=stop templateImage=" + getIcon(icon_pause))
    else:
        print("Stopped | terminal=false refresh=true bash=\"" +
          scriptFilepath + "\" param1=play templateImage=" + getIcon(icon_play))
    print("---")
    print("Open moode | href=" + moodeUrl)
else:
    print("| templateImage=" + getIcon(icon_offline))
    print("---")
    print("Moode is offline")