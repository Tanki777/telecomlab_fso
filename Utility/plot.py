import numpy as np
import matplotlib.pyplot as plt


def plot_psk_constellation(modulation='QPSK', figsize=(8, 8)):
    """
    Plot constellation points on a unit circle for PSK modulation schemes.
    
    Parameters:
    -----------
    modulation : str
        The modulation scheme: 'BPSK', 'QPSK', '8PSK', or '16PSK'
    figsize : tuple
        Figure size (width, height)
    
    Returns:
    --------
    fig, ax : matplotlib figure and axes objects
    """
    # Define number of constellation points and bits per symbol
    modulation_configs = {
        'BPSK': {'M': 2, 'bits': 1},
        'QPSK': {'M': 4, 'bits': 2},
        '8PSK': {'M': 8, 'bits': 3},
        '16PSK': {'M': 16, 'bits': 4}
    }
    
    if modulation.upper() not in modulation_configs:
        raise ValueError(f"Unsupported modulation: {modulation}. Choose from {list(modulation_configs.keys())}")
    
    config = modulation_configs[modulation.upper()]
    M = config['M']
    bits_per_symbol = config['bits']
    
    # Generate constellation points on unit circle
    angles = 2 * np.pi * np.arange(M) / M + np.pi/M
    
    # For BPSK, typically use 0° and 180°
    if modulation.upper() == 'BPSK':
        angles = np.array([0, np.pi])
    
    # Calculate I and Q components
    I = np.cos(angles)
    Q = np.sin(angles)
    
    # Create bit labels
    if M == 2:
        bit_labels = ['0', '1']
    elif M == 4:
        bit_labels = ['11', '01', '00', '10']
    elif M == 8:
        bit_labels = ['000', '100', '001', '101', '111', '011', '010', '110']
    elif M == 16:
        bit_labels = ['0000', '0001', '0011', '0010', '0110', '0111', '0101', '0100',
                      '1100', '1101', '1111', '1110', '1010', '1011', '1001', '1000']
    
    # Create the plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot unit circle
    circle = plt.Circle((0, 0), 1, fill=False, color='gray', linestyle='--', linewidth=1.5)
    ax.add_patch(circle)
    
    # Plot constellation points
    ax.scatter(I, Q, s=200, c='lightblue', marker='o', zorder=3, edgecolors='darkblue', linewidths=2)
    
    # Add bit labels to each point
    for i, q, label in zip(I, Q, bit_labels):
        offset = 0.15  # Offset for label placement
        ax.annotate(label, (i, q), 
                   xytext=(i * (1 + offset), q * (1 + offset)),
                   fontsize=12, fontweight='bold',
                   ha='center', va='center',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    # Draw axes through origin
    ax.axhline(y=0, color='k', linewidth=0.8)
    ax.axvline(x=0, color='k', linewidth=0.8)
    
    # Set equal aspect ratio and limits
    ax.set_aspect('equal')
    limit = 1.5
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    
    # Labels and title
    ax.set_xlabel('In-Phase (I)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Quadrature (Q)', fontsize=12, fontweight='bold')
    #ax.set_title(f'{modulation.upper()} Constellation Diagram', fontsize=14, fontweight='bold')
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    return fig, ax


if __name__ == '__main__':
    # Example usage: plot all PSK variants
    modulations = ['BPSK', 'QPSK', '8PSK', '16PSK']
    
    for mod in modulations:
        fig, ax = plot_psk_constellation(mod)
        plt.show()
