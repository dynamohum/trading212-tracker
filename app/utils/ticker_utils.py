def normalize_to_yfinance(t212_ticker):
    """
    Attempts to convert Trading212 internal ticker format to Yahoo Finance format.
    """
    t = t212_ticker
    
    # Common Suffixes
    if t.endswith('_US_EQ'):
        return t.replace('_US_EQ', '')
    
    # UK (London)
    if t.endswith('l_EQ'):
        return t.replace('l_EQ', '.L')
        
    # France (Paris)
    if t.endswith('p_EQ'):
        return t.replace('p_EQ', '.PA')
        
    # Germany (Xetra, Frankfurt)
    if t.endswith('d_EQ'):
        return t.replace('d_EQ', '.DE')
        
    # Spain (Madrid)
    if t.endswith('e_EQ'):
        return t.replace('e_EQ', '.MC')
        
    # Netherlands (Amsterdam)
    if t.endswith('n_EQ'):
        return t.replace('n_EQ', '.AS')

    # Generic _EQ stripping
    if t.endswith('_EQ'):
        return t.replace('_EQ', '')
        
    return t
