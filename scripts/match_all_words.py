def search_all(df, col, *words):
    """
    Return a sub-DataFrame of those rows whose Name column match all the words.
    source: https://stackoverflow.com/a/22624079/3349443
    """
    import numpy as np

    return df[np.logical_and.reduce([df[col].str.contains(word) for word in words])]